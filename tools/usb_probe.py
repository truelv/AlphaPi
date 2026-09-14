"""探测 USB CDC 串口：尝试多种 DTR/RTS 组合与波特率，抓取设备输出.

用法:
    python usb_probe.py COM11
    python usb_probe.py COM11 5 6000     # 每轮读 5 秒，总超时 6000ms

背景:
    Arduino / TinyUSB 类 CDC 通常只有在 DTR 置位时才把数据发给主机；
    而 ESP32 ROM 的 USB-Serial-JTAG 则相反，DTR/RTS 用于触发复位。
    因此这里把四组组合都试一遍。
"""
import sys
import time

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM11"
SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0

COMBOS = [
    ("DTR=1 RTS=0", True, False),
    ("DTR=0 RTS=1", False, True),
    ("DTR=1 RTS=1", True, True),
    ("DTR=0 RTS=0", False, False),
]


def try_combo(port, dtr, rts, secs):
    try:
        ser = serial.Serial(port, 115200, timeout=0.2)
    except Exception as exc:
        return None, str(exc)
    ser.setDTR(dtr)
    ser.setRTS(rts)
    time.sleep(0.5)
    ser.reset_input_buffer()
    ser.write(b"\x03\r\n")
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        data = ser.read(512)
        if data:
            buf += data
            end = time.time() + 1.0
    ser.setDTR(False)
    ser.setRTS(False)
    ser.close()
    return buf, None


def main():
    print("probing %s ..." % PORT)
    for label, dtr, rts in COMBOS:
        data, err = try_combo(PORT, dtr, rts, SECS)
        if err:
            print("[%s] OPEN FAILED: %s" % (label, err))
            return
        print("[%s] %d bytes" % (label, len(data)))
        if data:
            sys.stdout.write(data.decode("utf-8", "replace")[:2000])
            print()
    print("done.")


if __name__ == "__main__":
    main()
