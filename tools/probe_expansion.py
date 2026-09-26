"""AlphaPi 外接扩展板只读探测工具。

三种模式（全程只读 / 不写寄存器、不驱动执行器）：

    python tools/probe_expansion.py COM11 scan    # 扫多组 SoftI2C 引脚对 + 只读寄存器快照
    python tools/probe_expansion.py COM11 pins    # 全 GPIO 指纹：ADC + 上拉/下拉电平
    python tools/probe_expansion.py COM11         # 默认 scan

用法要点：
  - COM11（ESP32-S3 原生 USB CDC）需要 DTR=1；pyserial 打开端口默认已置位，脚本不再翻转。
  - `pins` 模式用于判断「扩展板到底把哪些 GPIO 拉住了」：
      上拉读 0 / 下拉读 1  => 外部强驱动，说明该脚接到了扩展板上的器件
      两边都读 1 或都读 0  => 悬空（上拉时 1，下拉时 0）
  - 发现 I2C 从机后，先查文档确认寄存器语义再写，别直接写（可能驱动电机）。

输出同时落盘 board_dump/expansion_cap.txt（原始缓冲）。
"""
import os
import re
import serial
import sys
import time

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM11"
MODE = sys.argv[2] if len(sys.argv) > 2 else "scan"
BAUD = 115200

# 候选引脚对：8/9 是固件里写死的扩展 I2C；4/5、6/7 是历史版本的总线；
# 其余为常见 GPIO。刻意避开 0(strapping)、19-32(flash/psram/屏) 等脚。
PAIRS = [(8, 9), (4, 5), (6, 7), (1, 2), (10, 11), (12, 13), (14, 15)]

# 指纹扫描范围：0/19-32 不动（strapping + flash/psram + 屏总线）
DIGITAL_PINS = list(range(1, 19)) + list(range(33, 49))
ADC_PINS = list(range(1, 19))

SCAN_PAYLOAD = """\
print("EXP_START")
import machine, ubinascii
pairs = %r
found = []
for sda, scl in pairs:
    try:
        bus = machine.SoftI2C(sda=machine.Pin(sda), scl=machine.Pin(scl), freq=100000)
        devs = bus.scan()
    except Exception as e:
        print("BUS sda%%d scl%%d ERR %%s" %% (sda, scl, e))
        continue
    print("BUS sda%%d scl%%d -> %%s" %% (sda, scl, [hex(x) for x in devs]))
    for d in devs:
        found.append((sda, scl, bus, d))
for sda, scl, bus, d in found:
    print("DEV 0x%%02x @ sda%%d/scl%%d" %% (d, sda, scl))
    row = []
    for r in range(0, 0x30):
        try:
            row.append(ubinascii.hexlify(bus.readfrom_mem(d, r, 1)).decode())
        except Exception:
            row.append("..")
    print("  regs: " + " ".join(row))
if not found:
    print("NO_I2C_DEVICE")
print("EXP_END")
""" % (PAIRS,)

PINS_PAYLOAD = """\
print("EXP_START")
import machine
print("FREQ=" + str(machine.freq()))
adc = {}
for n in %r:
    try:
        a = machine.ADC(machine.Pin(n))
        a.atten(machine.ADC.ATTN_11DB)
        adc[n] = a.read_u16()
    except Exception:
        adc[n] = -1
print("ADC16 " + repr(adc))
pu = {}
pd = {}
for n in %r:
    try:
        pu[n] = machine.Pin(n, machine.Pin.IN, machine.Pin.PULL_UP).value()
    except Exception:
        pu[n] = -1
for n in %r:
    try:
        pd[n] = machine.Pin(n, machine.Pin.IN, machine.Pin.PULL_DOWN).value()
    except Exception:
        pd[n] = -1
print("PULLUP   " + repr(pu))
print("PULLDOWN " + repr(pd))
print("DRIVEN   " + repr([n for n in pu if pu[n] != -1 and pd[n] != -1 and pu[n] == 0 and pd[n] == 1]))
print("FLOAT    " + repr([n for n in pu if pu[n] != -1 and pd[n] != -1 and pu[n] == 1 and pd[n] == 0]))
print("EXP_END")
""" % (ADC_PINS, DIGITAL_PINS, DIGITAL_PINS)

PAYLOAD = PINS_PAYLOAD if MODE == "pins" else SCAN_PAYLOAD


def try_enter_raw(ser):
    ser.write(b"\x03")
    time.sleep(0.4)
    ser.write(b"\x03")
    time.sleep(0.4)
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
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2.0)
    ok = False
    for _ in range(6):
        if try_enter_raw(ser):
            ok = True
            break
        time.sleep(0.5)
    if not ok:
        print("NO_RAW")
        ser.close()
        return
    code = PAYLOAD.encode()
    i = 0
    while i < len(code):
        ser.write(code[i:i + 32])
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
    end = time.time() + 45.0
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"EXP_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    try:
        os.makedirs("board_dump", exist_ok=True)
        with open("board_dump/expansion_cap.txt", "w", encoding="utf-8") as f:
            f.write(repr(buf))
    except Exception:
        pass
    starts = [m.start() for m in re.finditer("EXP_START", txt)]
    end_idx = txt.rfind("EXP_END")
    out = ""
    if starts and end_idx >= 0:
        out = txt[starts[-1] + len("EXP_START"):end_idx].strip("\r\n ")
    print("PORT=%s MODE=%s" % (PORT, MODE))
    print(out if out else "(no output) RAW=" + repr(txt[:400]))
    ser.close()


if __name__ == "__main__":
    main()
