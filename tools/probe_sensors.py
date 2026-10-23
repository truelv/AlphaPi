"""扩展板传感器端口探针（只读 / 不驱动执行器）。

用途：给 PH2.0 扩展板接上积木传感器后，确认「固件端口号 / GPIO」上能看到什么。

端口号约定（第 2 代 ESP32-S3，反汇编 `controlBoardAlphaPiOne` 确认）：
    `ReadPin / WritePin / ReadAdc / WritePwm` 的参数**就是 GPIO 号**
    —— 内部实现是 `pin_map[port] = Pin(port)`，没有第二张换算表。
    所以本脚本里的「端口 N」== GPIO N。

四个双线端口（超声波 / 红外接收 / 心率血氧三者共用）：
    端口 1: t=GPIO10 r=GPIO11      端口 2: t=GPIO12 r=GPIO13
    端口 3: t=GPIO14 r=GPIO17      端口 4: t=GPIO18 r=GPIO48

用法:
    python tools/probe_sensors.py COM11 scan           # 默认：全部安全脚 ADC + 数字电平
    python tools/probe_sensors.py COM11 adc 1,2,5,6    # 指定端口的模拟量（0-1023）
    python tools/probe_sensors.py COM11 pin 4,10,11    # 指定端口的数字电平
    python tools/probe_sensors.py COM11 i2c 1,2,3,4    # 用双线端口号扫 I2C（r=SDA, t=SCL）
    python tools/probe_sensors.py COM11 pair           # 只打印端口契约表（不连板子）

判读:
    - 模拟类（雨滴 / 红外测距 / 电位器）：看 adc 列是否随环境变化。
    - 数字类（人体红外 / 触摸 / 温湿度 / 按键）：看 pullup / pulldown 两列
      —— 插上后两列读到同一个值 = 该脚被外部器件拉住（有东西在线）。
    - I2C 类（心率血氧 / 红外接收）：i2c 模式扫到地址即在线
      （心率血氧 MAX30102 默认 0x57，红外接收模块 0x22）。

安全边界:
    默认不碰 GPIO0(strapping) / 3(N32 UART TX) / 19,20(USB) / 26-32(Flash/PSRAM)
    / 33-37(屏 + 电源使能) / 38-42(SPI 屏) / 43,44(日志口)。
    确实要测被排除的脚时，用 `adc` / `pin` 显式传端口号。
"""
import os
import re
import sys
import time

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM11"
MODE = sys.argv[2] if len(sys.argv) > 2 else "scan"
ARG = sys.argv[3] if len(sys.argv) > 3 else ""
BAUD = 115200

# 安全脚（第 2 代 ESP32-S3，已排除 strapping / UART / USB / Flash / 屏 / 日志口）
SAFE_PORTS = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21, 47, 48]

# 双线端口 -> (t, r)，与固件 controlBoardAlphaPiOne.PinPair 一致
PAIRS = {1: (10, 11), 2: (12, 13), 3: (14, 17), 4: (18, 48)}


def parse_ports(default):
    if ARG:
        return [int(x) for x in ARG.split(",")]
    return list(default)


SCAN_PAYLOAD = """\
print("PRB_START")
import machine
for n in %r:
    try:
        a = machine.ADC(machine.Pin(n)); a.atten(machine.ADC.ATTN_11DB)
        v = a.read_u16() >> 6
    except Exception:
        v = -1
    try:
        pu = machine.Pin(n, machine.Pin.IN, machine.Pin.PULL_UP).value()
    except Exception:
        pu = -1
    try:
        pd = machine.Pin(n, machine.Pin.IN, machine.Pin.PULL_DOWN).value()
    except Exception:
        pd = -1
    print("PORT %%d adc=%%d pullup=%%d pulldown=%%d" %% (n, v, pu, pd))
print("PRB_END")
"""

ADC_PAYLOAD = """\
print("PRB_START")
import machine
for n in %r:
    try:
        a = machine.ADC(machine.Pin(n)); a.atten(machine.ADC.ATTN_11DB)
        v = a.read_u16() >> 6
    except Exception as e:
        v = "ERR %%s" %% e
    print("PORT %%d adc=%%s" %% (n, v))
print("PRB_END")
"""

PIN_PAYLOAD = """\
print("PRB_START")
import machine
for n in %r:
    try:
        pu = machine.Pin(n, machine.Pin.IN, machine.Pin.PULL_UP).value()
    except Exception:
        pu = -1
    try:
        pd = machine.Pin(n, machine.Pin.IN, machine.Pin.PULL_DOWN).value()
    except Exception:
        pd = -1
    try:
        dn = machine.Pin(n, machine.Pin.IN).value()
    except Exception:
        dn = -1
    print("PORT %%d pullup=%%d pulldown=%%d float=%%d" %% (n, pu, pd, dn))
print("PRB_END")
"""

I2C_PAYLOAD = """\
print("PRB_START")
import machine
pairs = %r
for k in %r:
    t, r = pairs[k]
    try:
        bus = machine.SoftI2C(sda=machine.Pin(r), scl=machine.Pin(t), freq=100000)
        devs = [hex(x) for x in bus.scan()]
    except Exception as e:
        devs = "ERR %%s" %% e
    print("PAIR %%d scl(t)=%%d sda(r)=%%d -> %%s" %% (k, t, r, devs))
print("PRB_END")
"""


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


def run_payload(ser, payload, timeout=30.0):
    code = payload.encode()
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
    end = time.time() + timeout
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"PRB_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    starts = [m.start() for m in re.finditer("PRB_START", txt)]
    end_idx = txt.rfind("PRB_END")
    if starts and end_idx >= 0:
        return txt[starts[-1] + len("PRB_START"):end_idx].strip("\r\n ")
    return ""


def print_pairs():
    print("双线端口契约（固件 controlBoardAlphaPiOne.PinPair）：")
    for k in sorted(PAIRS):
        t, r = PAIRS[k]
        print("  端口 %d:  t=GPIO%-3d  r=GPIO%-3d" % (k, t, r))
    print("")
    print("单线传感器：端口号 == GPIO 号（底板对应 P 口）。")
    print("  ReadPin(端口) / ReadAdc(端口) / WritePin(端口,值) / WritePwm(端口,值)")
    print("  温湿度 dht.DHT11(Pin(端口)) / 舵机 PWM(Pin(端口)) / RGB NeoPixel(Pin(端口), n)")


def main():
    if MODE == "pair":
        print_pairs()
        return

    if MODE == "i2c":
        ports = parse_ports(sorted(PAIRS.keys()))
        payload = I2C_PAYLOAD % (PAIRS, ports)
    elif MODE == "adc":
        payload = ADC_PAYLOAD % (parse_ports(SAFE_PORTS),)
    elif MODE == "pin":
        payload = PIN_PAYLOAD % (parse_ports(SAFE_PORTS),)
    else:
        payload = SCAN_PAYLOAD % (parse_ports(SAFE_PORTS),)

    print("PORT=%s MODE=%s" % (PORT, MODE))
    print("-" * 60)
    print("提示：手柄板 GPIO10-13 是按键、GPIO17 是板载灯带；屏占 33-42，别往那儿插。")
    print("-" * 60)

    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2.0)
    ok = False
    for _ in range(6):
        if try_enter_raw(ser):
            ok = True
            break
        time.sleep(0.5)
    if not ok:
        print("NO_RAW（串口被占用 / 板子没上电？）")
        ser.close()
        return

    out = run_payload(ser, payload)
    ser.close()

    try:
        os.makedirs("board_dump", exist_ok=True)
        with open("board_dump/sensor_probe.txt", "w", encoding="utf-8") as f:
            f.write(out)
    except Exception:
        pass

    print(out if out else "(no output)")


if __name__ == "__main__":
    main()
