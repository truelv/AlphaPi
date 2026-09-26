"""联网滚动时钟 —— 量子兔 AlphaPi（COM13 / 第 1 代 ESP32-C3）

硬件：5x5 红点阵（经 N32）+ 3 按键 + 14 颗 WS2812 灯带 + N32 音频
功能：WiFi 联网 → NTP 对时 → 点阵滚动显示 时间/日期/星期；灯带做秒进度条；整点报时

部署（板子上需要 clock.py 与 main.py 两个文件）：
    python tools/repl_probe.py COM13 put projects/AlphaPiClock/board/clock.py clock.py
    python tools/repl_probe.py COM13 put projects/AlphaPiClock/board/main.py  main.py
    python tools/repl_probe.py COM13 reset

按键：
    A(10) = 切换模式（时间 -> 日期 -> 星期）
    B(20) = 强制重新 NTP 对时
    C(21) = 整点报时开 / 关

注意：本文件顶层没有任何阻塞调用，`run()` 里是死循环，只能靠 Ctrl-C 退出。
"""

import time

import network
import ntptime

import control_board_v1 as cb
import actuator_led as al
from basic import DataStruct

# ==================== 配置（改这里） ====================

# ⚠️ WiFi 凭据**不要写在本文件里**：本仓库有公开 remote（github.com/truelv/AlphaPi）。
#    请放到同目录的 clock_secrets.py（已在 .gitignore 中忽略），内容形如：
#        WIFI_SSID = "TP-LINK_XXXX"
#        WIFI_PASS = "xxxxxxxx"
#    板子上也需要这个文件；找不到就自动进入离线模式（用 OFFLINE_START 起走）。
#    模板见同目录 clock_secrets.example.py。
try:
    from clock_secrets import WIFI_SSID, WIFI_PASS
except ImportError:
    WIFI_SSID = ""
    WIFI_PASS = ""

WIFI_TIMEOUT_S = 20     # 联网超时（秒）

TZ_HOURS = 8            # 时区偏移（小时），中国大陆 = 8
NTP_HOST = "ntp.aliyun.com"
NTP_RETRY = 3
DNS_SERVER = "114.114.114.114"   # 规避官方手册记录的 WiFi DNS -202 问题

SCROLL_MS = 8000        # 同一段文字重复滚动的间隔（毫秒）；N32 滚完一轮约 3～4 秒
CHIME_ON_HOUR = True    # 整点是否报时（播放 alert.dat）
CHIME_FILE = "alert.dat"

USE_STRIP = True        # 没接灯带就设 False
STRIP_PIN = 5           # 灯带数据脚（固定 14 颗）
STRIP_BRIGHTNESS = 100  # 0-100
STRIP_COLOR = 0x00B34D  # 秒进度条颜色（偏暗的绿）

BUTTON_ACTIVE_HIGH = True   # 按键按下为高电平（固件用 Pin.IN + PULL_DOWN）
LOOP_MS = 20            # 主循环节拍

OFFLINE_START = (2026, 9, 26, 12, 0, 0)   # 离线模式起始时间（年, 月, 日, 时, 分, 秒）

# =======================================================


MODE_TIME, MODE_DATE, MODE_WEEK = 0, 1, 2
MODE_NAMES = ("TIME", "DATE", "WEEK")
WEEKDAY = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")


def log(msg):
    """串口日志（COM13 的 log 和 REPL 共用同一个 USB-Serial/JTAG，别刷太频）。"""
    print("[clock] " + str(msg))


# ----------------------------------------------------------------- 显示

def show(text):
    """在 5x5 点阵上滚动显示。N32 自己负责滚动，这里立即返回、不阻塞。"""
    try:
        cb.led_show_string_async(text)
    except Exception as exc:
        log("show failed: %s" % exc)


def clear():
    try:
        cb.led_show_bytes_async(bytearray([0, 0, 0, 0, 0]))
    except Exception as exc:
        log("clear failed: %s" % exc)


# ----------------------------------------------------------------- 灯带

strip_ok = False
strip_last_lit = -1


def strip_init():
    global strip_ok
    if not USE_STRIP:
        return
    try:
        al.InitNP(STRIP_PIN)
        al.SetBrightness(DataStruct(STRIP_BRIGHTNESS))
        for i in range(14):
            al.setPixelColor(DataStruct(i), DataStruct(0))
        strip_ok = True
        log("strip ready on GPIO%d" % STRIP_PIN)
    except Exception as exc:
        strip_ok = False
        log("strip init failed: %s" % exc)


def strip_tick(sec):
    """把"当前秒"映射成灯带进度条（只在格子数变化时重画，避免每秒刷 14 次）。"""
    global strip_ok, strip_last_lit
    if not strip_ok:
        return
    lit = sec * 14 // 60
    if lit == strip_last_lit:
        return
    strip_last_lit = lit
    try:
        for i in range(14):
            al.setPixelColor(DataStruct(i), DataStruct(STRIP_COLOR if i < lit else 0))
    except Exception as exc:
        strip_ok = False
        log("strip write failed: %s" % exc)


# ----------------------------------------------------------------- 时间

def local_now():
    """本地时间 8 元组：(年,月,日,时,分,秒,星期(0=周一),年积日)"""
    return time.localtime(time.time() + TZ_HOURS * 3600)


def text_for(mode, t):
    if mode == MODE_TIME:
        return "%02d:%02d" % (t[3], t[4])
    if mode == MODE_DATE:
        return "%02d-%02d" % (t[1], t[2])
    return WEEKDAY[t[6]]


def set_rtc_offline():
    """离线模式：把 OFFLINE_START（按**本地时间**理解）写进 RTC。

    板子 RTC 存的是 UTC，`time.localtime()` 也按 UTC 解释，
    所以先把本地时间转成 epoch、减去时区偏移，再拆回 UTC 元组写入。
    （MicroPython 的 epoch 是 2000-01-01，与 CPython 不同。）
    """
    try:
        import machine
        y, mo, d, h, mi, s = OFFLINE_START
        wd = 0
        mktime = getattr(time, "mktime", None)
        if mktime is not None:
            u = time.localtime(mktime((y, mo, d, h, mi, s, 0, 0)) - TZ_HOURS * 3600)
            y, mo, d, h, mi, s, wd = u[0], u[1], u[2], u[3], u[4], u[5], u[6]
        machine.RTC().datetime((y, mo, d, wd, h, mi, s, 0))
        t = local_now()
        log("rtc set (offline): %04d-%02d-%02d %02d:%02d:%02d"
            % (t[0], t[1], t[2], t[3], t[4], t[5]))
    except Exception as exc:
        log("rtc set failed: %s" % exc)


# ----------------------------------------------------------------- 联网

def wifi_connect():
    if not WIFI_SSID:
        log("no ssid configured -> offline mode")
        return False
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if wlan.isconnected():
            log("wifi already up: %s" % wlan.ifconfig()[0])
            return True
        log("connecting to %s ..." % WIFI_SSID)
        show("WiFi")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        deadline = WIFI_TIMEOUT_S * 2
        while deadline > 0:
            if wlan.isconnected():
                break
            time.sleep_ms(500)
            deadline -= 1
        if not wlan.isconnected():
            log("wifi connect FAILED (timeout)")
            return False
        ip, mask, gw, _ = wlan.ifconfig()
        # 手册记录的坑：不显式设 DNS 时解析会失败（errno -202）
        wlan.ifconfig((ip, mask, gw, DNS_SERVER))
        log("wifi ok: ip=%s gw=%s dns=%s" % (ip, gw, DNS_SERVER))
        return True
    except Exception as exc:
        log("wifi error: %s" % exc)
        return False


def ntp_sync():
    show("SYNC")
    ntptime.host = NTP_HOST
    for attempt in range(NTP_RETRY):
        try:
            ntptime.settime()
            t = local_now()
            log("ntp ok: %04d-%02d-%02d %02d:%02d:%02d" % (t[0], t[1], t[2], t[3], t[4], t[5]))
            return True
        except Exception as exc:
            log("ntp attempt %d/%d failed: %s" % (attempt + 1, NTP_RETRY, exc))
            time.sleep_ms(800)
    return False


# ----------------------------------------------------------------- 按键

btn_prev = [0, 0, 0]


def buttons_pressed():
    """刷新按键并返回"本次新按下"的序号列表（0=A, 1=B, 2=C）——边沿检测，长按不重复触发。"""
    try:
        cb.UpdateButtonStatus()
        cur = [cb.pa_last_status, cb.pb_last_status, cb.pc_last_status]
    except Exception as exc:
        log("button read failed: %s" % exc)
        return []
    if not BUTTON_ACTIVE_HIGH:
        cur = [0 if v else 1 for v in cur]
    pressed = []
    for i in range(3):
        if cur[i] and not btn_prev[i]:
            pressed.append(i)
        btn_prev[i] = cur[i]
    return pressed


# ----------------------------------------------------------------- 主程序

def run():
    global btn_prev
    # 注意：日志一律用 ASCII —— Windows 控制台是 GBK，中文字符串会乱码/报错
    log("boot: AlphaPi COM13 rolling clock")

    strip_init()
    clear()

    online = wifi_connect()
    synced = online and ntp_sync()
    if not synced:
        log("running offline")
        set_rtc_offline()
        show("oFF")

    mode = MODE_TIME
    chime_enabled = CHIME_ON_HOUR

    t = local_now()
    last_hour = t[3]
    last_min = t[4]
    last_sec = -1

    show(text_for(mode, t))
    last_show = time.ticks_ms()

    # 音频主循环泵：必须每帧 next() 一次，否则录音/播放全停
    sound_loop = cb.play_record_loop()

    btn_prev = [0, 0, 0]

    while True:
        next(sound_loop)
        t = local_now()

        for b in buttons_pressed():
            if b == 0:
                mode = (mode + 1) % 3
                show(text_for(mode, t))
                last_show = time.ticks_ms()
                log("mode -> %s" % MODE_NAMES[mode])
            elif b == 1:
                if online and ntp_sync():
                    t = local_now()
                    last_hour = t[3]
                    last_min = t[4]
                    show(text_for(mode, t))
                    last_show = time.ticks_ms()
                else:
                    log("resync skipped (offline)")
                    show("oFF")
            elif b == 2:
                chime_enabled = not chime_enabled
                show("On" if chime_enabled else "oFF")
                log("chime -> %s" % ("on" if chime_enabled else "off"))

        # 分钟变化 或 到达重复滚动周期 -> 重刷一遍文字（N32 会重新滚）
        if t[4] != last_min or time.ticks_diff(time.ticks_ms(), last_show) > SCROLL_MS:
            last_min = t[4]
            show(text_for(mode, t))
            last_show = time.ticks_ms()

        # 秒进度条（strip_tick 内部只在格子数变化时才重画）
        if t[5] != last_sec:
            last_sec = t[5]
            strip_tick(t[5])

        # 整点报时（小时跳变时触发一次，开机首帧不会误报）
        if t[3] != last_hour:
            last_hour = t[3]
            if chime_enabled:
                log("hour chime %02d:00" % t[3])
                try:
                    cb.play(CHIME_FILE)      # 阻塞约 0.6 秒，可接受
                except Exception as exc:
                    log("chime failed: %s" % exc)
                show(text_for(mode, local_now()))
                last_show = time.ticks_ms()

        time.sleep_ms(LOOP_MS)
