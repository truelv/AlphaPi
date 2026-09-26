import serial, time, sys, os, re, base64

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

# 把 .mpy 二进制分块 base64 编码后打印（避免大文件在设备上内存不足），host 端拼接解码
PAYLOAD = (
    'import ubinascii\n'
    'CHUNK=512\n'
    'print("FULL_START")\n'
    'for fn in ["basic.mpy","autoMotionOne.mpy","remoteControlActuatorOne.mpy","remoteControlSensorOne.mpy","steeringEngineActuatorAlphaPiOne.mpy","max30102.mpy"]:\n'
    ' try:\n'
    '  f=open(fn,"rb")\n'
    '  print("####"+fn)\n'
    '  while True:\n'
    '   b=f.read(CHUNK)\n'
    '   if not b: break\n'
    '   print(ubinascii.b2a_base64(b).decode().strip())\n'
    '  f.close()\n'
    ' except Exception as e:\n'
    '  print("####"+fn+":ERR:"+str(e)+"\\n")\n'
    'print("FULL_END")\n'
)

def exec_and_capture(ser):
    code = PAYLOAD.encode()
    i = 0
    while i < len(code):
        chunk = code[i:i+32]
        ser.write(chunk)
        time.sleep(0.01)
        deadline = time.time() + 0.5
        while time.time() < deadline:
            d = ser.read(256)
            if d:
                deadline = time.time() + 0.5
        i += 32
    time.sleep(0.3)
    ser.reset_input_buffer()
    ser.write(b"\x04")
    buf = b""
    end = time.time() + 40.0
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"FULL_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    try:
        with open("board_dump/full_cap.txt", "w", encoding="utf-8") as dbg:
            dbg.write("LEN=%d\n" % len(buf))
            dbg.write(repr(buf))
    except Exception:
        pass
    # 保存原始全文便于排查
    try:
        with open("board_dump/full_out.txt", "w", encoding="utf-8") as f:
            f.write(txt)
    except Exception:
        pass
    # 解码 base64 块
    out_dir = "board_dump/dumped"
    os.makedirs(out_dir, exist_ok=True)
    starts = [m.start() for m in re.finditer("FULL_START", txt)]
    end_idx = txt.rfind("FULL_END")
    body = ""
    if starts and end_idx >= 0:
        body = txt[starts[-1] + len("FULL_START"):end_idx]
    saved = []
    for part in body.split("####"):
        part = part.strip("\r\n ")
        if not part:
            continue
        lines = part.split("\n")
        fn = lines[0].strip()
        if fn.endswith(":ERR:"):
            print("  !! %s" % fn)
            continue
        # 逐行（每块）独立解码后拼接：每块各自补 '=' ，整体解码会在第一个 '=' 处截断
        try:
            data = b""
            for ln in lines[1:]:
                ln = ln.strip()
                if ln:
                    data += base64.b64decode(ln)
            path = os.path.join(out_dir, fn)
            with open(path, "wb") as f:
                f.write(data)
            saved.append("%s (%d bytes)" % (fn, len(data)))
        except Exception as e:
            print("  decode fail %s: %s" % (fn, e))
    return saved

def main():
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2.0)
    ok = False
    for attempt in range(6):
        if try_enter_raw(ser):
            ok = True
            break
        time.sleep(0.5)
    if not ok:
        print("NO_RAW")
        ser.close()
        sys.exit(0)
    print("RAW_OK")
    saved = exec_and_capture(ser)
    if saved:
        print("SAVED:")
        for s in saved:
            print("  " + s)
    else:
        print("NO_FILES")
    ser.close()

if __name__ == "__main__":
    main()
