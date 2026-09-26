# remote_pad.py —— 用手柄板（COM11 / ESP32-S3）当 AlphaPi 小车「无线遥控手柄」
#
# 硬件（板载，见 remoteControlSensorOne）：
#   摇杆 X = ADC8，Y = ADC7（中位约 512）      电位器 = ADC6（当速度上限旋钮）
#   按键 A/B/C/D = GPIO13/12/11/10（PULL_UP，按下为 0）
#   ST7735 屏 160x128，16px 字体（一行最多 10 字符）
#
# 通信协议（与网页端完全一致，向 UDP 1000 广播）：
#   {"token":"", "message":"drive", "value":"<左轮>,<右轮>"}   # 摇杆比例驱动，-100~100
#   {"token":"", "message":"开爪"/"合爪"/"开灯"/"关灯"/"停", "value":""}
#
# 安装（一次性）：
#   1) 本文件传到板子根目录
#   2) 板子 main.py 改为：
#          import remote_pad
#          remote_pad.main(static_buf)      # static_buf 由 boot.py 提前分配，务必复用
#   3) 复位板子
#
# 操作：
#   摇杆推哪走哪（比例差速，松手自动停）；电位器调速度上限（20~100）
#   A=开爪  B=合爪  C=开灯/关灯  D=急停

import socket
import time

import controlBoardAlphaPiOne as board
import remoteControlSensorOne as pad
from basic import DataStruct

# ================= 可配置 =================
WIFI_SSID = "TP-LINK_F18C"      # 与小车同一局域网（boot.py 已连，这里兜底）
WIFI_PASSWORD = "18143463550"

CAR_PORT = 1000                 # 小车监听端口
TOKEN = ""                      # 与小车一致（默认空）
BROADCAST = "255.255.255.255"   # 广播，无需知道小车 IP

DEADZONE = 0.16                 # 摇杆死区（比例），防止中位漂移导致爬行
INVERT_X = False                # 推右却左转 -> 改 True
INVERT_Y = False                # 推上却后退 -> 改 True
POT_MIN_SPD = 20                # 电位器最低速
POT_MAX_SPD = 100               # 电位器最高速

LOOP_MS = 20                    # 主循环 50Hz（按键响应）
SEND_EVERY = 4                  # 每 4 次循环发一次（约 80ms）
SCREEN_EVERY = 12               # 每 12 次循环刷屏（约 240ms）
CAR_TIMEOUT_MS = 6000           # 多久没收到小车心跳算离线
# =========================================

_rx = None
_tx = None
_tft = None
_prev_line = {}
_btns_prev = [0, 0, 0, 0]
_light_on = False
_car_seen = 0
_cx = 512.0
_cy = 512.0


def _clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


# ---------------- 屏幕 ----------------
def _line(y, text):
    """只在内容变化时重画一行（160 宽、16 高）。"""
    if _tft is None:
        return
    if _prev_line.get(y) == text:
        return
    _prev_line[y] = text
    try:
        _tft.fillrect((0, y), (160, 16), _tft.BLACK)
        board.showStringWithXY(0, y, text)
    except Exception:
        pass


def _screen(ip, spd, tag, li, ri, jx, jy):
    _line(0, "CAR ON" if _car_online() else "CAR --")
    _line(16, "SPD%3d %s" % (spd, tag))
    _line(32, "L%+3d R%3d" % (li, ri))
    _line(48, "X%3d Y%3d" % (jx, jy))
    _line(80, "A/B=CLAW")
    _line(96, "C=LED %s" % ("ON" if _light_on else "OFF"))
    _line(112, "D=STOP")


def _car_online():
    return _car_seen and time.ticks_diff(time.ticks_ms(), _car_seen) < CAR_TIMEOUT_MS


# ---------------- 网络 ----------------
def _ensure_wifi():
    try:
        import network
        w = network.WLAN(network.STA_IF)
        if w.isconnected():
            return w.ifconfig()[0]
    except Exception:
        return ""
    try:
        board.connectWifi(DataStruct(WIFI_SSID), DataStruct(WIFI_PASSWORD))
        import network
        return network.WLAN(network.STA_IF).ifconfig()[0]
    except Exception:
        return ""


def _udp_send(msg, value=""):
    try:
        data = ('{"token":"%s","message":"%s","value":"%s"}' % (TOKEN, msg, value)).encode()
        _tx.sendto(data, (BROADCAST, CAR_PORT))
    except Exception:
        pass


def _udp_poll():
    """收小车的 hb / ack，用于在屏上显示在线状态。"""
    global _car_seen
    for _ in range(6):
        try:
            data, _addr = _rx.recvfrom(256)
        except Exception:
            return
        try:
            txt = data.decode()
            if '"message": "hb"' in txt or '"message":"hb"' in txt:
                _car_seen = time.ticks_ms()
            elif '"message": "ack"' in txt or '"message":"ack"' in txt:
                _car_seen = time.ticks_ms()
        except Exception:
            pass


# ---------------- 摇杆 ----------------
def _calibrate():
    """开电时以当前摇杆位置为"中位"（实测中位约 532/530，并非正好 512）。"""
    global _cx, _cy
    sx = 0
    sy = 0
    n = 0
    for _ in range(24):
        pad.Update()
        st = pad.status_list
        sx += st[4]
        sy += st[5]
        n += 1
        time.sleep_ms(10)
    if n:
        _cx = sx / n
        _cy = sy / n


def main(static_buf=None):
    global _tft, _rx, _tx, _light_on

    board.init()
    if static_buf is not None:
        try:
            board.InitBackground_buf(static_buf)
        except Exception:
            pass

    try:
        _tft = board.tft
        _tft.fill(_tft.BLACK)
    except Exception:
        _tft = None

    ip = _ensure_wifi()
    print("remote_pad wifi ip=" + str(ip))

    # 预热 + 中位标定（第一帧 ADC 会跳变，必须丢弃）
    for _ in range(5):
        pad.Update()
        time.sleep_ms(20)
    _calibrate()
    print("remote_pad center x=%.1f y=%.1f" % (_cx, _cy))

    _rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        _rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass
    try:
        _rx.bind(("", CAR_PORT))
    except Exception as e:
        print("bind fail " + str(e))
    try:
        _rx.setblocking(False)
    except Exception:
        pass

    _tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 注意：本固件(MicroPython 1.19/esp32)的 socket 模块**没有 SO_BROADCAST 常量**，
    # 直接引用会 AttributeError 把主程序打断。实测不设该选项也能向 255.255.255.255 广播
    # （板载 controlBoardAlphaPiOne 库本身就没设，心跳照样能广播出去），故容错处理即可。
    try:
        _tx.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except Exception:
        pass

    _line(64, "READY")
    print("remote_pad ready -> udp %s:%d" % (BROADCAST, CAR_PORT))

    tag = "STOP"
    li = ri = 0
    spd = 60
    i = 0
    last_dbg = None

    while True:
        pad.Update()
        st = pad.status_list
        jx = st[4]
        jy = st[5]
        pot = st[14]

        # ---- 速度上限（电位器）----
        spd = POT_MIN_SPD + (POT_MAX_SPD - POT_MIN_SPD) * _clamp(pot, 0, 1023) // 1023

        # ---- 摇杆 -> 比例差速 ----
        fx = _clamp((jx - _cx) / 512.0, -1.0, 1.0)
        fy = _clamp((jy - _cy) / 512.0, -1.0, 1.0)
        if -DEADZONE < fx < DEADZONE:
            fx = 0.0
        if -DEADZONE < fy < DEADZONE:
            fy = 0.0
        if INVERT_X:
            fx = -fx
        if INVERT_Y:
            fy = -fy

        l = _clamp(fy - fx, -1.0, 1.0)
        r = _clamp(fy + fx, -1.0, 1.0)
        s = spd / 100.0
        li = int(l * s * 100 + (0.5 if l * s >= 0 else -0.5))
        ri = int(r * s * 100 + (0.5 if r * s >= 0 else -0.5))

        if fx == 0.0 and fy == 0.0:
            tag = "STOP"
        elif fy > 0:
            tag = "FWD" if fx == 0 else ("FR" if fx > 0 else "FL")
        elif fy < 0:
            tag = "BACK" if fx == 0 else ("BR" if fx > 0 else "BL")
        else:
            tag = "RIGHT" if fx > 0 else "LEFT"

        # ---- 调试：摇杆/输出变化时打印一行（用于核对方向正负）----
        if (li, ri) != last_dbg:
            last_dbg = (li, ri)
            print("PAD x=%d y=%d pot=%d -> L%+d R%+d %s" % (jx, jy, pot, li, ri, tag))

        # ---- 按键（边沿触发，st[0]=A st[1]=B st[2]=C st[3]=D）----
        for k in range(4):
            cur = 1 if st[k] else 0
            if cur and not _btns_prev[k]:
                if k == 0:
                    _udp_send("开爪")
                    print("KEY A -> 开爪")
                elif k == 1:
                    _udp_send("合爪")
                    print("KEY B -> 合爪")
                elif k == 2:
                    _light_on = not _light_on
                    _udp_send("开灯" if _light_on else "关灯")
                    print("KEY C -> light %s" % _light_on)
                else:
                    _udp_send("停")
                    print("KEY D -> 停")
            _btns_prev[k] = cur

        # ---- 周期发送状态 ----
        # 必须"持续发送"（不能只在变化时发）：小车端有 900ms 失联保护，
        # 摇杆保持不动时若不发包，小车会被判定失联而自动停车。
        if i % SEND_EVERY == 0:
            _udp_send("drive", "%d,%d" % (li, ri))

        if i % SCREEN_EVERY == 0:
            _screen("", spd, tag, li, ri, jx, jy)

        _udp_poll()
        i += 1
        time.sleep_ms(LOOP_MS)


def run():
    main(getattr(__import__("__main__"), "static_buf", None))
