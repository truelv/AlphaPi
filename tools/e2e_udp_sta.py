"""STA 模式端到端测试：主动复位板子 -> 等连上 WiFi 拿 IP -> 从局域网发 UDP -> 读串口看 CMD。"""
import serial, time, socket, json, threading, re

def p(x):
    print(str(x).encode("ascii", "backslashreplace").decode())

CMDS = [("上", "35"), ("停", ""), ("左", "30"), ("停", ""),
        ("右", "30"), ("停", ""), ("开爪", ""), ("合爪", ""), ("停", "")]

ser = serial.Serial("COM10", 115200, timeout=0.2)
time.sleep(1.0)
ser.write(b"\x03"); time.sleep(0.3)
ser.write(b"\x03"); time.sleep(0.3)
ser.reset_input_buffer()
ser.write(b"\x01"); time.sleep(0.3)                 # 进 raw REPL
ser.write(b"import machine\nmachine.reset()\x04")   # 主动复位

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
if not ip:
    p("serial tail:")
    p(buf.decode("utf-8", "replace")[-500:])
    ser.close()
    raise SystemExit

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_all():
    for msg, val in CMDS:
        try:
            s.sendto(json.dumps({"token": "", "message": msg, "value": val}).encode(), (ip, 1000))
            p("SENT %s %s" % (msg, val))
        except Exception as e:
            p("send err " + str(e))
        time.sleep(0.9)


t = threading.Thread(target=send_all)
t.start()
end = time.time() + 14
while time.time() < end:
    d = ser.read(256)
    if d:
        buf += d
t.join(timeout=1)
ser.close()
p("=== serial tail ===")
p(buf.decode("utf-8", "replace")[-700:])
p("CMD_COUNT=%d" % buf.count(b"CMD"))
