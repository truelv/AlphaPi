"""测试 开灯/关灯：复位板子 -> 发指令 -> 看串口 CMD 与是否异常。"""
import time, re, threading, socket, json
import serial

CMDS = [("开灯", ""), ("关灯", ""), ("开灯", "")]

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
print("BOARD_IP=%s" % ip)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def worker():
    for msg, val in CMDS:
        s.sendto(json.dumps({"token": "", "message": msg, "value": val}).encode(), (ip, 1000))
        print("SENT " + msg.encode("ascii", "backslashreplace").decode())
        time.sleep(1.5)


t = threading.Thread(target=worker)
t.start()
end = time.time() + 10
while time.time() < end:
    d = ser.read(256)
    if d:
        buf += d
t.join(timeout=1)
ser.close()
txt = buf.decode("utf-8", "replace")
print("CMD_COUNT=%d" % txt.count("CMD"))
print("HAS_TRACEBACK=%s" % ("Traceback" in txt))
print(txt[-300:].encode("ascii", "backslashreplace").decode())
