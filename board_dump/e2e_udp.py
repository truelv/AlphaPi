"""端到端测试：向板子(192.168.4.1:1000)发 UDP 遥控命令，同时读板子串口看是否收到（打印 CMD）。"""
import serial, time, socket, json, threading

PORT = "COM10"
BOARD_IP = "192.168.4.1"
PORT_UDP = 1000

CMDS = [("上", "35"), ("停", ""), ("左", "30"), ("停", ""),
        ("右", "30"), ("停", ""), ("开爪", ""), ("合爪", ""), ("停", "")]


def sender():
    time.sleep(2.5)   # 等串口稳定/板子启动
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for msg, val in CMDS:
        try:
            s.sendto(json.dumps({"token": "", "message": msg, "value": val}).encode(), (BOARD_IP, PORT_UDP))
            print("SENT  %s %s" % (msg, val))
        except Exception as e:
            print("send err", e)
        time.sleep(0.9)
    s.close()


ser = serial.Serial(PORT, 115200, timeout=0.2)
t = threading.Thread(target=sender, daemon=True)
t.start()
end = time.time() + 16
buf = b""
while time.time() < end:
    d = ser.read(256)
    if d:
        buf += d
        line = d.decode("utf-8", "replace").strip()
        if line:
            print("SER: " + repr(line))
t.join(timeout=1)
ser.close()
print("=== serial dump ===")
print(buf.decode("utf-8", "replace"))
print("CMD_COUNT=%d" % buf.count(b"CMD"))
