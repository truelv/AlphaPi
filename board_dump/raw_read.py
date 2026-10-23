"""软复位板子并原样捕获串口输出（不发 Ctrl-C，不打断 main.py）。"""
import sys
import time

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM3"
SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0

ser = serial.Serial(PORT, 115200, timeout=0.2)
ser.setDTR(False)
ser.setRTS(False)
time.sleep(0.3)
ser.write(b"\x04")  # Ctrl-D: 软复位，main.py 重新跑
buf = b""
end = time.time() + SECS
while time.time() < end:
    d = ser.read(1024)
    if d:
        buf += d
ser.close()
sys.stdout.write(buf.decode("utf-8", "replace"))
