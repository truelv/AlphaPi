"""验证树莓派网页服务控车：板子串口监控 + 通过 SSH 让 Pi 的本地网页 API 发指令。"""
import time, re, threading
import serial, paramiko

HOST, USER, PWD = "192.168.1.27", "pi", "wangchen"


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

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=PWD, timeout=10)


def pi_api(message, value=""):
    cmd = ("curl -s -X POST -H 'Content-Type: application/json' "
           "--data '{\"message\":\"%s\",\"value\":\"%s\"}' http://127.0.0.1:8080/api" % (message, value))
    _, out, _ = cli.exec_command(cmd, timeout=8)
    r = out.read().decode("utf-8", "replace")
    p("PI %s %s -> %s" % (message, value, r))


def worker():
    pi_api("drive", "25,25"); time.sleep(1.2)
    pi_api("drive", "30,-30"); time.sleep(1.2)
    pi_api("停"); time.sleep(0.4)
    pi_api("开爪"); time.sleep(0.8)
    pi_api("合爪"); time.sleep(0.8)
    pi_api("停")


t = threading.Thread(target=worker)
t.start()
end = time.time() + 12
while time.time() < end:
    d = ser.read(256)
    if d:
        buf += d
t.join(timeout=1)
ser.close()
cli.close()
p("CMD_COUNT=%d" % buf.count(b"CMD"))
p(buf.decode("utf-8", "replace")[-350:].encode("ascii", "backslashreplace").decode())
