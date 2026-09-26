"""分块上传文件到 MicroPython 板子（避免一次性编译大常量导致 MemoryError）。
用法：python upload_chunked.py <本地文件> [板子上文件名]
原理：进入 raw REPL，先 open('文件','wb')，再逐块 a2b_base64 后 write（块间共享 __main__ 全局）。
"""
import serial, time, sys, os, base64

PORT = "COM10"
BAUD = 115200
CHUNK = 360   # base64 字符数/块（≈270 字节）

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

def raw_exec(ser, code, timeout=4.0):
    ser.write(code.encode("utf-8") + b"\x04")
    buf = b""
    end = time.time() + timeout
    while time.time() < end:
        d = ser.read(128)
        if d:
            buf += d
            if buf.endswith(b">"):
                break
            end = time.time() + 0.6
    return buf

def main():
    local = sys.argv[1]
    remote = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(local)
    with open(local, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()

    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2.0)
    if not try_enter_raw(ser):
        print("NO_RAW"); ser.close(); sys.exit(1)

    try:
        r = raw_exec(ser, "import ubinascii,gc\ngc.collect()")
        if b"Traceback" in r:
            print("import fail:", r); ser.close(); sys.exit(1)
        raw_exec(ser, "f=open('%s','wb')" % remote)
        n = 0
        for i in range(0, len(b64), CHUNK):
            part = b64[i:i + CHUNK]
            r = raw_exec(ser, "f.write(ubinascii.a2b_base64('%s'))" % part)
            if b"Traceback" in r:
                print("chunk %d fail: %s" % (n, r)); ser.close(); sys.exit(1)
            n += 1
        raw_exec(ser, "f.close()")
        r = raw_exec(ser, "print('SZ %%d' %% len(open('%s','rb').read()))" % remote)
        ser.write(b"\x02")  # 退出 raw
        print("LOCAL %s (%d bytes) -> %s | chunks=%d" % (local, len(data), remote, n))
        for tok in r.split(b"\r\n"):
            t = tok.strip(b">\x04 ")
            if t:
                print("  " + t.decode("utf-8", "replace"))
        if ("SZ %d" % len(data)).encode() in r:
            print("UPLOAD OK")
        else:
            print("UPLOAD MAY FAILED")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
