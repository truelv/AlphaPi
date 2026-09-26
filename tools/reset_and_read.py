"""复位板子并读取启动输出（用于抓 STA 模式下的 IP）。"""
import serial, time

ser = serial.Serial("COM10", 115200, timeout=0.5)
time.sleep(1.0)
ser.write(b"\x03"); time.sleep(0.3)
ser.write(b"\x03"); time.sleep(0.3)
ser.reset_input_buffer()
ser.write(b"\x01"); time.sleep(0.3)      # 进 raw
ser.write(b"import machine\nmachine.reset()\x04")
buf = b""
end = time.time() + 30
while time.time() < end:
    d = ser.read(256)
    if d:
        buf += d
        if b"remote_car ready" in buf:
            break
try:
    with open("board_dump/sta_cap.txt", "w", encoding="utf-8") as f:
        f.write(buf.decode("utf-8", "replace"))
except Exception:
    pass
print(buf.decode("utf-8", "replace"))
ser.close()
