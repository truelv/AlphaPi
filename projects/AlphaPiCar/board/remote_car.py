# remote_car.py —— AlphaPi-One 小车「WiFi 遥控」封装（板子端）
#
# 两种模式（改下面的 MODE）：
#   MODE="sta" —— 板子连你家路由器，进入局域网（推荐）。PC/Pi/手机同一网络即可直接控制。
#   MODE="ap"  —— 板子自己开热点，客户端连热点后控制。
#
# 安装（随系统启动）：
#   1) 本文件传到板子根目录。
#   2) 板子 main.py 改为：
#          import remote_car
#          remote_car.main(static_buf)     # static_buf 由 boot.py 提前分配，务必复用
#   3) 复位板子。
#
# 通信协议：向 UDP 端口 1000 发 JSON
#       {"token": "<TOKEN>", "message": "<命令>", "value": "<值>"}
#   message：
#       上 / 下 / 左 / 右        —— 固定速度方向（value 可选速度 -100~100）
#       停                       —— 停止
#       drive                    —— 比例驱动，value="左轮,右轮"（各 -100~100），用于摇杆
#       开爪 / 合爪
#       开灯 / 关灯
#   目标地址：STA 模式用板子 IP 或局域网广播 255.255.255.255；AP 模式用 192.168.4.1。

import time
import autoMotionOne as car
import controlBoardAlphaPiOne as board
from basic import DataStruct

# ================= 可配置 =================
MODE = "sta"                 # "sta"=连路由器 / "ap"=自开热点
WIFI_SSID = "TP-LINK_F18C"   # 你家 WiFi 名称（STA 模式用）
WIFI_PASSWORD = "18143463550"  # 你家 WiFi 密码（STA 模式用）

AP_SSID = "AlphaPi01"        # 自开热点名（AP 模式用）
AP_PASSWORD = "12345678"

TOKEN = ""                   # 若设置，客户端 token 必须一致
DEFAULT_SPEED = 50           # 默认速度 1~100
AUTO_STOP_MS = 900           # >0：超时无命令则自动停（失联保护）；0=锁存（收到"停"才停）
                             # 网页端(150~200ms)与手柄端(80ms)都是流式发送，故 900ms 安全
HB_MS = 2000                 # 心跳间隔(ms)：定期广播状态，供上位机显示"在线"
# =========================================

MOVE = ("上", "下", "左", "右", "drive")
OTHER = ("停", "开爪", "合爪", "开灯", "关灯")


def get_buffer():
    """复用 boot.py 已分配的 static_buf；取不到再尝试自建。"""
    try:
        import __main__
        b = getattr(__main__, "static_buf", None)
        if b:
            return b
    except Exception:
        pass
    return bytearray(40960)


def _speed(msg):
    raw = board.getBroadcastValue(DataStruct(msg))
    try:
        if raw:
            return max(-100, min(100, int(float(raw))))
    except Exception:
        pass
    return DEFAULT_SPEED


def _set_light(r, g, b):
    """把所有 WS2812 像素设为指定颜色（0,0,0 即关闭）。"""
    try:
        car.SetBrightness(100)
        c = car.packRGBd(r, g, b)          # 返回 DataStruct
        for i in range(car.np.n):
            car.setPixelColor(i, c)
    except Exception:
        pass


def _power(l, r):
    """驱动左右轮。

    实车左右电机接线与"逻辑左/右"相反，故此处统一对调一次：
    对前进/后退无影响，但把左转/右转纠正过来（方向键与摇杆一并生效）。
    """
    car.set_all_power(DataStruct(r), DataStruct(l))


def apply(msg):
    """执行一条命令。"""
    if msg == "上":
        s = abs(_speed(msg)); _power(s, s)
    elif msg == "下":
        s = abs(_speed(msg)); _power(-s, -s)
    elif msg == "左":
        s = abs(_speed(msg)); _power(s, -s)
    elif msg == "右":
        s = abs(_speed(msg)); _power(-s, s)
    elif msg == "drive":
        raw = str(board.getBroadcastValue(DataStruct("drive")))
        try:
            l, r = raw.split(",")
            l = max(-100, min(100, int(float(l))))
            r = max(-100, min(100, int(float(r))))
            _power(l, r)
        except Exception:
            pass
    elif msg == "停":
        car.stop_motor(DataStruct(2))
    elif msg == "开爪":
        car.set_claw(DataStruct(1))
    elif msg == "合爪":
        car.set_claw(DataStruct(0))
    elif msg == "开灯":
        _set_light(255, 255, 255)
    elif msg == "关灯":
        _set_light(0, 0, 0)


def start_network():
    """按 MODE 建立网络，并打印本机地址。"""
    if MODE == "sta":
        board.connectWifi(DataStruct(WIFI_SSID), DataStruct(WIFI_PASSWORD))
        import network
        print("WIFI STA: " + str(network.WLAN(network.STA_IF).ifconfig()))
    else:
        board.openHotspot(DataStruct(AP_SSID), DataStruct(AP_PASSWORD))
        print("WIFI AP: " + AP_SSID + " | udp 1000 | token: " + repr(TOKEN))


def _my_ip():
    try:
        import network
        return network.WLAN(network.STA_IF).ifconfig()[0]
    except Exception:
        return ""


def _notify(message, value=""):
    """向上位机广播一条状态（心跳 / 指令回执），供其显示在线状态。"""
    try:
        board.broadcastWithValue(DataStruct(message), DataStruct(value))
    except Exception:
        pass


def main(static_buf=None):
    if static_buf is None:
        static_buf = get_buffer()
    board.init()
    board.InitBackground_buf(static_buf)
    if TOKEN:
        board.setToken(DataStruct(TOKEN))
    start_network()
    car.stop_motor(DataStruct(2))
    myip = _my_ip()
    print("remote_car ready | udp port 1000 | " + myip)

    last_move = 0
    last_hb = 0
    while True:
        board.Update()          # 内部收 UDP
        moved = False
        for msg in MOVE + OTHER:
            if board.hasBroadcast(DataStruct(msg)):
                apply(msg)
                print("CMD " + msg)
                _notify("ack", msg)
                moved = True
                if msg in MOVE:
                    last_move = time.ticks_ms()
        if AUTO_STOP_MS and (not moved) and last_move and \
           time.ticks_diff(time.ticks_ms(), last_move) > AUTO_STOP_MS:
            car.stop_motor(DataStruct(2))
            last_move = 0
        if time.ticks_diff(time.ticks_ms(), last_hb) >= HB_MS:
            last_hb = time.ticks_ms()
            _notify("hb", myip)
        time.sleep_ms(20)


def run():
    """REPL 便捷入口。"""
    main(get_buffer())
