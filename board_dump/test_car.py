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

# 低速实测：前进/后退各 0.7s + 爪子开合；读编码器位置验证轮子转动
PAYLOAD = """\
print("MOT_START")
import time
import autoMotionOne as car
from basic import DataStruct
print("READY")
def pos(m):
    try:
        return car.get_position(m)
    except Exception as e:
        return "err:" + str(e)
print("L0=" + str(pos(car.MOTOR_L)))
car.set_all_power(DataStruct(30), DataStruct(30))
time.sleep_ms(700)
car.stop_motor(DataStruct(2))
time.sleep_ms(300)
print("L1=" + str(pos(car.MOTOR_L)))
print("FWD_OK")
car.set_all_power(DataStruct(-30), DataStruct(-30))
time.sleep_ms(700)
car.stop_motor(DataStruct(2))
time.sleep_ms(300)
print("BWD_OK")
car.set_claw(DataStruct(0))
time.sleep_ms(900)
car.set_raw_power(car.MOTOR_Z, 0)
time.sleep_ms(300)
print("CLAW_A_OK")
car.set_claw(DataStruct(1))
time.sleep_ms(900)
car.set_raw_power(car.MOTOR_Z, 0)
time.sleep_ms(300)
print("CLAW_B_OK")
car.stop_motor(DataStruct(2))
car.set_raw_power(car.MOTOR_Z, 0)
print("MOT_END")
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
    end = time.time() + 25.0
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"MOT_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    try:
        with open("board_dump/car_test_cap.txt", "w", encoding="utf-8") as f:
            f.write(repr(buf))
    except Exception:
        pass
    starts = [m.start() for m in re.finditer("MOT_START", txt)]
    end_idx = txt.rfind("MOT_END")
    out = ""
    if starts and end_idx >= 0:
        out = txt[starts[-1] + len("MOT_START"):end_idx].strip("\r\n ")
    with open("board_dump/car_test_out.txt", "w", encoding="utf-8") as f:
        f.write(out)
    print("TEST_SAVED bytes=%d" % len(out))
    print(out)
    ser.close()

if __name__ == "__main__":
    main()
