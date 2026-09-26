#!/usr/bin/env python3
# car_remote_client.py —— PC/手机端：向 AlphaPi-One 小车发送 UDP 遥控命令
#
# 前提：本机与板子在同一局域网（板子 STA 模式连你家 WiFi，如 192.168.1.16）。
#       板子 IP 看板子串口启动打印 "WIFI STA: ('192.168.1.16', ...)"。
#
# 用法：
#   python car_remote_client.py 上              # 前进（默认广播，无需知道板子 IP）
#   python car_remote_client.py 上 80           # 带速度
#   python car_remote_client.py --ip 192.168.1.16 左   # 直连指定 IP
#   python car_remote_client.py --shell         # 交互模式
#   python car_remote_client.py --demo          # 自动演示
#
# 命令：上 / 下 / 左 / 右 / 停 / 开爪 / 合爪 / 开灯 / 关灯

import socket
import sys
import time
import json

HOST = "255.255.255.255"   # 默认广播；可用 --ip 指定板子 IP
PORT = 1000
TOKEN = ""


def send(msg, value="", host=HOST):
    payload = json.dumps({"token": TOKEN, "message": msg, "value": str(value)}).encode("utf-8")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(payload, (host, PORT))
    s.close()
    print("-> %s %s @ %s" % (msg, value if value != "" else "", host))


def shell(host):
    print("命令：上/下/左/右/停/开爪/合爪/开灯/关灯 ；q 退出")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line in ("q", "quit", "exit"):
            break
        parts = line.split()
        send(parts[0], parts[1] if len(parts) > 1 else "", host)
    send("停", "", host)


def demo(host):
    for _ in range(3):
        send("上", 50, host); time.sleep(0.4)
    send("停", "", host); time.sleep(0.6)
    send("左", 40, host); time.sleep(0.5); send("停", "", host); time.sleep(0.4)
    send("右", 40, host); time.sleep(0.5); send("停", "", host); time.sleep(0.4)
    send("开爪", "", host); time.sleep(1.0)
    send("合爪", "", host); time.sleep(1.0)
    send("停", "", host)


if __name__ == "__main__":
    args = sys.argv[1:]
    host = HOST
    if "--ip" in args:
        i = args.index("--ip")
        host = args[i + 1]
        del args[i:i + 2]
    if args and args[0] == "--shell":
        shell(host)
    elif args and args[0] == "--demo":
        demo(host)
    elif args:
        send(args[0], args[1] if len(args) >= 2 else "", host)
    else:
        print(__doc__)
