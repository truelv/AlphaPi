"""手柄板（COM11）诊断：抓完整启动日志 + 检查 WiFi / 模块导入 / UDP 发送.

用法:
    python pad_diag.py [COM11] [boot_secs]

流程:
    1) 软复位（Ctrl-D），把 boot.py / main.py 的完整输出打出来（含异常回溯）
    2) Ctrl-C 停下主程序，进 raw REPL 检查:
       WiFi 状态、remote_pad 能否导入、socket 广播发送是否成功、board.tft 是否存在
"""

import sys
import time

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM11"
BOOT_SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 18.0

DIAG = (
    "import network\n"
    "w = network.WLAN(network.STA_IF)\n"
    "print('wifi_active', w.active(), 'connected', w.isconnected())\n"
    "print('ifconfig', w.ifconfig())\n"
    "try:\n"
    "    import remote_pad\n"
    "    print('remote_pad import OK')\n"
    "except Exception as e:\n"
    "    print('remote_pad import ERR', type(e).__name__, e)\n"
    "try:\n"
    "    import socket\n"
    "    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n"
    "    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)\n"
    "    s.sendto(b'{\"token\":\"\",\"message\":\"drive\",\"value\":\"0,0\"}', ('255.255.255.255', 1000))\n"
    "    print('SEND OK')\n"
    "except Exception as e:\n"
    "    print('SEND ERR', type(e).__name__, e)\n"
    "try:\n"
    "    import controlBoardAlphaPiOne as b\n"
    "    print('board has_tft', hasattr(b, 'tft'))\n"
    "except Exception as e:\n"
    "    print('board ERR', type(e).__name__, e)\n"
    "try:\n"
    "    import os\n"
    "    print('files', sorted([f for f in os.listdir() if f.endswith('.py')]))\n"
    "except Exception as e:\n"
    "    print('ls ERR', e)\n"
    "print('DIAG_END')\n"
)


def read_for(ser, secs, quiet_after=2.0):
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        data = ser.read(1024)
        if data:
            buf += data
            sys.stdout.write(data.decode("utf-8", "replace"))
            sys.stdout.flush()
    return buf


def main():
    ser = serial.Serial(PORT, 115200, timeout=0.2)
    ser.setDTR(True)
    ser.setRTS(False)
    time.sleep(0.3)
    ser.reset_input_buffer()

    print("=== phase 1: soft reset, capture boot log (%ds) ===" % BOOT_SECS)
    ser.write(b"\x02")
    time.sleep(0.2)
    ser.write(b"\x04")
    read_for(ser, BOOT_SECS)
    print("\n=== phase 1 done ===")

    print("=== phase 2: ctrl-C + diagnostics ===")
    ser.write(b"\x03\x03")
    time.sleep(0.6)
    ser.reset_input_buffer()
    ser.write(b"\x01")
    time.sleep(0.4)
    ser.reset_input_buffer()
    for i in range(0, len(DIAG), 128):
        ser.write(DIAG[i:i + 128].encode())
        time.sleep(0.03)
    ser.write(b"\x04")
    read_for(ser, 15.0)
    print("\n=== phase 2 done ===")
    ser.close()


if __name__ == "__main__":
    main()
