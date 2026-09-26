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

# 验证 remote_car 板子端：init + 开热点 + 收包循环若干轮
PAYLOAD = """\
print("RC_START")
import time
import __main__
buf = getattr(__main__, "static_buf", None)
print("HAS_BUF=" + str(buf is not None))
print("BUF_LEN=" + str(len(buf) if buf else -1))
import remote_car as rc
import autoMotionOne as car
import controlBoardAlphaPiOne as board
from basic import DataStruct
if buf is None:
    buf = bytearray(20000)
    print("ALLOC_SMALL")
board.init()
board.InitBackground_buf(buf)
print("BG_OK")
board.openHotspot(DataStruct("AlphaPi01"), DataStruct("12345678"))
time.sleep_ms(1500)
import network
print("AP=" + str(network.WLAN(network.AP_IF).ifconfig()))
rc.apply("停")
for k in range(10):
    board.Update()
    time.sleep_ms(50)
print("RC_LOOP_OK")
car.stop_motor(DataStruct(2))
print("RC_END")
"""

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
    end = time.time() + 30.0
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"RC_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    try:
        with open("board_dump/rc_cap.txt", "w", encoding="utf-8") as f:
            f.write(repr(buf))
    except Exception:
        pass
    starts = [m.start() for m in re.finditer("RC_START", txt)]
    end_idx = txt.rfind("RC_END")
    out = ""
    if starts and end_idx >= 0:
        out = txt[starts[-1] + len("RC_START"):end_idx].strip("\r\n ")
    print("RC_SAVED bytes=%d" % len(out))
    print(out)
    ser.close()

if __name__ == "__main__":
    main()
