"""通过 raw REPL 把本地文件上传到 MicroPython 板子。
用法：python upload_file.py <本地文件> [板子上文件名]
原理：把文件 base64 后作为一行 Python 代码发送，在板子上解码写盘。
"""
import serial, time, sys, os, base64, re

PORT = "COM10"
BAUD = 115200

def try_enter_raw(ser):
    ser.write(b"\x03"); time.sleep(0.4)
    ser.write(b"\x03"); time.sleep(0.4)
    ser.reset_input_buffer()
    ser.write(b"\x01")
    buf = b""
    end = time.time() + 3.0
    while time.time() < end:
        d = ser.read(200)
        if d:
            buf += d
            if b"raw REPL" in buf:
                return True
    return False

def main():
    local = sys.argv[1]
    remote = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(local)
    with open(local, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    payload = (
        "import ubinascii\n"
        "print('UP_START')\n"
        "d=ubinascii.a2b_base64('" + b64 + "')\n"
        "f=open('" + remote + "','wb')\n"
        "f.write(d)\n"
        "f.close()\n"
        "print('WROTE %d' % len(d))\n"
        "print('SIZE %d' % len(open('" + remote + "','rb').read()))\n"
        "print('UP_END')\n"
    )
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2.0)
    ok = False
    for _ in range(6):
        if try_enter_raw(ser):
            ok = True
            break
        time.sleep(0.5)
    if not ok:
        print("NO_RAW"); ser.close(); sys.exit(1)
    code = payload.encode()
    i = 0
    while i < len(code):
        ser.write(code[i:i+48])
        time.sleep(0.01)
        deadline = time.time() + 0.4
        while time.time() < deadline:
            d = ser.read(256)
            if d:
                deadline = time.time() + 0.4
        i += 48
    time.sleep(0.3)
    ser.reset_input_buffer()
    ser.write(b"\x04")
    buf = b""
    end = time.time() + 20.0
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"UP_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    print("LOCAL  %s (%d bytes)" % (local, len(data)))
    print("REMOTE %s" % remote)
    for m in re.finditer(r"(WROTE \d+|SIZE \d+|Traceback[^\n]*|[A-Za-z]*Error:[^\n]*)", txt):
        print("  " + m.group(1))
    if "SIZE %d" % len(data) in txt:
        print("UPLOAD OK")
    else:
        print("UPLOAD MAY FAILED")
        print(txt)
    ser.close()

if __name__ == "__main__":
    main()
