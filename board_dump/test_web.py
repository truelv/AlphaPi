"""网页层端到端测试：复位板子拿IP -> 起网页服务 -> HTTP 发指令 -> 读串口看 CMD。"""
import sys, os, time, re, json, threading, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import serial
import car_web


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

th = threading.Thread(target=lambda: car_web.serve(port=8080, board_ip=ip), daemon=True)
th.start()
time.sleep(1.0)


def api(message, value=""):
    body = json.dumps({"message": message, "value": value}).encode()
    req = urllib.request.Request("http://127.0.0.1:8080/api", data=body,
                                 headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=3).read()
    p("HTTP %s %s -> %s" % (message, value, r))


api("drive", "25,25"); time.sleep(1.2)
api("drive", "30,-30"); time.sleep(1.2)
api("停"); time.sleep(0.4)
api("开爪"); time.sleep(0.8)
api("合爪"); time.sleep(0.8)
api("停")

end = time.time() + 3
while time.time() < end:
    d = ser.read(256)
    if d:
        buf += d
ser.close()
p("CMD_COUNT=%d" % buf.count(b"CMD"))
p(buf.decode("utf-8", "replace")[-400:].encode("ascii", "backslashreplace").decode())
