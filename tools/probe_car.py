import serial, time, sys, os, re

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

# 只读探测车用 I2C 上的 0x20 电机控制器：确认扫描、各电机寄存器、0x00-0x3C 快照
PAYLOAD = """\
print("CAR_START")
import machine, ubinascii
i = machine.SoftI2C(scl=machine.Pin(9), sda=machine.Pin(8), freq=100000)
print("scan=" + str([hex(x) for x in i.scan()]))
def rd(a, n):
    try:
        return ubinascii.hexlify(i.readfrom_mem(0x20, a, n)).decode()
    except Exception as e:
        return "ERR:" + str(e)
for base, name in [(0x20, "L"), (0x10, "R"), (0x30, "Z")]:
    print(name + " spd  @" + hex(base) + "=" + rd(base, 4))
    print(name + " pwr  @" + hex(base + 4) + "=" + rd(base + 4, 2))
    print(name + " pos  @" + hex(base + 8) + "=" + rd(base + 8, 8))
    print(name + " mode @" + hex(base + 12) + "=" + rd(base + 12, 2))
print("map:")
for a in range(0, 64):
    print("@" + hex(a) + "=" + rd(a, 1))
print("stab@0x28:")
for _ in range(6):
    print("s=" + rd(0x28, 4))
print("CAR_END")
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
            if b"CAR_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    try:
        with open("board_dump/car_cap.txt", "w", encoding="utf-8") as f:
            f.write(repr(buf))
    except Exception:
        pass
    starts = [m.start() for m in re.finditer("CAR_START", txt)]
    end_idx = txt.rfind("CAR_END")
    out = ""
    if starts and end_idx >= 0:
        out = txt[starts[-1] + len("CAR_START"):end_idx].strip("\r\n ")
    with open("board_dump/car_out.txt", "w", encoding="utf-8") as f:
        f.write(out)
    print("CAR_SAVED bytes=%d" % len(out))
    print(out)
    ser.close()

if __name__ == "__main__":
    main()
