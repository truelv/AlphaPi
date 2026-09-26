"""验证广播(255.255.255.255)与直连 IP 两种方式都能被板子收到。"""
import serial, time, socket, json, threading, re

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

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def send_all():
    # 1) 广播
    for msg in ("上", "下"):
        s.sendto(json.dumps({"token": "", "message": msg, "value": "30"}).encode(), ("255.255.255.255", 1000))
        p("BROADCAST " + msg)
        time.sleep(1.0)
    # 2) 直连 IP
    if ip:
        for msg in ("左", "右"):
            s.sendto(json.dumps({"token": "", "message": msg, "value": "30"}).encode(), (ip, 1000))
            p("DIRECT " + msg)
            time.sleep(1.0)
    s.sendto(json.dumps({"token": "", "message": "停", "value": ""}).encode(), (ip or "255.255.255.255", 1000))


t = threading.Thread(target=send_all)
t.start()
end = time.time() + 12
while time.time() < end:
    d = ser.read(256)
    if d:
        buf += d
t.join(timeout=1)
ser.close()
p("CMD_COUNT=%d" % buf.count(b"CMD"))
p(buf.decode("utf-8", "replace")[-400:].encode("ascii", "backslashreplace").decode())
