"""网页层端到端测试：复位板子拿IP -> 起网页服务 -> HTTP 发各方向指令 -> 读串口看 CMD。"""
import sys, os, time, re, json, threading, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "projects", "AlphaPiCar", "host"))
import serial
import car_web

PORT = 8090
CMDS = [("上", "40"), ("停", ""), ("下", "40"), ("停", ""),
        ("左", "40"), ("停", ""), ("右", "40"), ("停", ""),
        ("drive", "40,-40"), ("停", ""), ("开灯", ""), ("关灯", "")]


def p(x):
    print(str(x).encode("ascii", "backslashreplace").decode())


ser = serial.Serial("COM10", 115200, timeout=0.2)
time.sleep(1.0)
ser.write(b"\x03"); time.sleep(0.3)
ser.write(b"\x03"); time.sleep(0.3)
ser.reset_input_buffer()
ser.write(b"\x01"); time.sleep(0.3)
ser.write(b"import machine\nmachine.reset()\x04")

buf = b""
ip = None
end = time.time() + 35
while time.time() < end:
    d = ser.read(256)
    if d:
        buf += d
        s = buf.decode("utf-8", "replace")
        m = re.search(r"WIFI STA: \('([\d.]+)'", s)
        if m:
            ip = m.group(1)
        if "remote_car ready" in s:
            break
p("BOARD_IP=" + str(ip))

threading.Thread(target=lambda: car_web.serve(port=PORT, board_ip=ip), daemon=True).start()
time.sleep(1.0)


def api(message, value=""):
    body = json.dumps({"message": message, "value": value}).encode()
    req = urllib.request.Request("http://127.0.0.1:%d/api" % PORT, data=body,
                                 headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=3).read()
    p("HTTP %-6s %-8s -> %s" % (message.encode("ascii", "backslashreplace").decode(), value, r))


def worker():
    for msg, val in CMDS:
        api(msg, val)
        time.sleep(0.9)


t = threading.Thread(target=worker)
t.start()
end = time.time() + 16
while time.time() < end:
    d = ser.read(256)
    if d:
        buf += d
t.join(timeout=1)
ser.close()
txt = buf.decode("utf-8", "replace")
p("CMD_COUNT=%d  (期望 %d)" % (txt.count("CMD"), len(CMDS) - 2))  # 停 会合并
p("HAS_TRACEBACK=%s" % ("Traceback" in txt))
p(txt[-320:].encode("ascii", "backslashreplace").decode())
