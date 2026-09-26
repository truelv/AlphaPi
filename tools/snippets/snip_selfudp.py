import time
import __main__
import sys
if "remote_car" in sys.modules:
    del sys.modules["remote_car"]
import remote_car as rc
import controlBoardAlphaPiOne as board
import autoMotionOne as car
from basic import DataStruct
import socket, ujson, network

buf = getattr(__main__, "static_buf", None)
print("BUF=" + str(buf is not None))
board.init()
board.InitBackground_buf(buf)
board.openHotspot(DataStruct("AlphaPi01"), DataStruct("12345678"))
time.sleep_ms(1500)
print("AP=" + str(network.WLAN(network.AP_IF).ifconfig()))

# 先跑几轮 Update，让板子建立并绑定 UDP 接收 socket
for _ in range(3):
    board.Update()
    time.sleep_ms(100)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg = ujson.dumps({"token": "", "message": "上", "value": "40"})
for a in ("192.168.4.1", "127.0.0.1", "255.255.255.255"):
    try:
        s.sendto(msg.encode(), (a, 1000))
    except Exception as e:
        print("send " + a + " err " + str(e))
    time.sleep_ms(250)
    board.Update()
    print("to " + a + " HAS_UP=" + str(board.hasBroadcast(DataStruct("上"))) +
          " VAL=" + str(board.getBroadcastValue(DataStruct("上"))))
print("RC_END")
