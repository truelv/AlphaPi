"""在板子 raw REPL 上运行一个本地 .py 片段并抓取输出。
用法：python repl_eval.py <snippet.py>
抓取标记：自动在片段前后加 RUN_START / RUN_END 打印。
"""
import serial, time, sys, re

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
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        body = f.read()
    payload = 'print("RUN_START")\n' + body + '\nprint("RUN_END")\n'
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2.0)
    ok = False
    for _ in range(6):
        if try_enter_raw(ser):
            ok = True; break
        time.sleep(0.5)
    if not ok:
        print("NO_RAW"); ser.close(); sys.exit(1)
    code = payload.encode()
    i = 0
    while i < len(code):
        ser.write(code[i:i+32]); time.sleep(0.01)
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
    end = time.time() + 20.0
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"RUN_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    starts = [m.start() for m in re.finditer("RUN_START", txt)]
    end_idx = txt.rfind("RUN_END")
    out = ""
    if starts and end_idx >= 0:
        out = txt[starts[-1] + len("RUN_START"):end_idx].strip("\r\n ")
    print(out)
    if not out.strip():
        print("RAW=" + repr(txt))
    ser.close()

if __name__ == "__main__":
    main()
