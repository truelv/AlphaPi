"""AlphaPi 串口日志查看工具.

用法:
    python serial_log.py                      # 默认 COM10 @115200, 读 8 秒, 自动发 Ctrl-C
    python serial_log.py COM11 115200 10      # 指定端口 / 波特率 / 读取秒数
    python serial_log.py COM11 115200 8           # 游戏机（ESP32-S3 原生 CDC），默认已置 DTR
    python serial_log.py COM11 115200 --follow    # 一直盯着，Ctrl-C 退出
    python serial_log.py COM10 115200 8 --no-ctrl-c    # 只被动监听，不发送任何数据
    python serial_log.py COM10 115200 8 --hex          # 额外打印十六进制
    python serial_log.py COM10 115200 8 --no-dtr       # 少数需要 DTR=0 的设备

注意:
    - 同一时刻一个串口只能被一个程序打开，请先关闭 PuTTY / MobaXterm / VS Code 等已占用该口的工具。
    - COM11 游戏机（VID_303A:PID_4001）是 ESP32-S3 原生 USB CDC：实测只有 DTR=1 且 RTS=0
      时板子才会把数据发给主机，所以默认把 DTR 置位（--no-dtr 可拉低）。
    - 重要：这类设备一旦把 DTR 拉低，在同一个串口句柄里再拉高也回不来，必须重新打开串口。
      所以不要用带 DTR 开关的终端去反复切换。
    - ESP32-S3 的 ROM 引导日志固定为 115200；应用层日志可能使用其他波特率。
"""

import sys
import time

try:
    import serial
except ImportError:
    print("pyserial not installed, run: pip install pyserial")
    sys.exit(1)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}

    port = args[0] if len(args) > 0 else "COM10"
    baud = int(args[1]) if len(args) > 1 else 115200
    secs = float(args[2]) if len(args) > 2 else 8.0
    send_ctrl_c = "--no-ctrl-c" not in flags
    show_hex = "--hex" in flags
    keep_dtr = "--no-dtr" not in flags
    follow = "--follow" in flags

    try:
        ser = serial.Serial(port, baud, timeout=0.3)
    except Exception as exc:
        print("OPEN FAILED %s: %s" % (port, exc))
        print("提示: 该串口可能正被其他工具占用，请先关闭再试。")
        sys.exit(1)

    # COM11 游戏机（ESP32-S3 原生 USB CDC）必须 DTR=1 才会把数据发给主机，所以默认置位；
    # 少数需要 DTR=0 的设备用 --no-dtr。
    ser.setDTR(keep_dtr)
    ser.setRTS(False)
    time.sleep(0.3)

    if send_ctrl_c:
        print("OPENED %s @ %d, DTR=%d, sending Ctrl-C ..." % (port, baud, int(keep_dtr)))
        ser.write(b"\x03\x03\r\n")
    else:
        print("OPENED %s @ %d, DTR=%d, listening only ..." % (port, baud, int(keep_dtr)))

    end = None if follow else (time.time() + secs)
    total = 0
    try:
        while end is None or time.time() < end:
            data = ser.read(4096)
            if not data:
                continue
            total += len(data)
            if show_hex:
                sys.stdout.write("HEX> %s\n" % data.hex(" "))
            sys.stdout.write(data.decode("utf-8", "replace"))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass

    ser.close()
    print("\n--- %d bytes received ---" % total)


if __name__ == "__main__":
    main()
