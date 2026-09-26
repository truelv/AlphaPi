"""GPIO 逐脚翻转器：把扩展板「P 端口 -> GPIO」映射表测出来。

用途：外接底板（模拟 I/O / 数字 IO / 电机 三类 PH2.0 口）是纯扇出，固件里没有映射表，
      只能实测。本脚本让板子逐个 GPIO 输出高/低电平，你用万用表电压档（或 LED+电阻）
      把表笔固定在某个端口的信号脚上，看指针什么时候跳，对照本地日志的时间戳即可对出
      「这个口 = 哪个 GPIO」。

用法:
    python tools/pin_sweeper.py COM11                # 默认安全脚位集合，每脚 2 个周期
    python tools/pin_sweeper.py COM11 --pins 1,2,4   # 只扫指定脚
    python tools/pin_sweeper.py COM11 --hold 2.0 --cycles 3

安全边界（默认集合已排除以下脚，别随便加）:
    GPIO0        strapping / 启动模式
    GPIO3        UART1 TX -> N32 音频协处理器
    GPIO19/20    USB D-/D+（驱动它 = 立刻掉线）
    GPIO26-32    Flash / PSRAM
    GPIO38-42    ST7735 屏总线（CS/DC/RST/SCK/MOSI）
    GPIO43/44    串口日志
    默认集合里的 GPIO4(震动马达) / GPIO17(板载 WS2812) 会被反复翻转，属正常现象。

测量姿势:
    - 万用表打直流电压档，黑笔接端口的 G（地），红笔接 S（信号）。
    - 表笔别松手，盯住读数在 3.3V / 0V 之间跳变的时刻。
    - 判读：日志里某一行的 GPIO 号旁的时间戳，正好对上你看到跳动的时间。
    - 更好用：把表笔固定在一个口上，脚本跑完一轮（所有脚各跳 2 次），
      记录「第 k 次跳变」；日志里第 k 个 HIGH 事件就是对应的 GPIO。
"""
import re
import serial
import sys
import time

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM11"
BAUD = 115200

# 翻转后不会碰到关键外设的脚位（见文件头「安全边界」）
SAFE_PINS = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18]

HOLD = 2.0
CYCLES = 2
if "--hold" in sys.argv:
    HOLD = float(sys.argv[sys.argv.index("--hold") + 1])
if "--cycles" in sys.argv:
    CYCLES = int(sys.argv[sys.argv.index("--cycles") + 1])
PINS = SAFE_PINS
if "--pins" in sys.argv:
    PINS = [int(x) for x in sys.argv[sys.argv.index("--pins") + 1].split(",")]

# 注意：这里用一个"手动喂"的节奏 —— 每步由主机发一条短命令，板子执行一个阶段。
# 好处是每一步都有确定的时刻，日志时间戳可直接对表笔读数。
STEP = """\
import machine, time
p = machine.Pin(%d, machine.Pin.OUT, value=%d)
time.sleep_ms(%d)
print("STEP g%d=%d")
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


def run_step(ser, code, timeout=8.0):
    ser.write(b"\x03\x03")
    time.sleep(0.15)
    ser.reset_input_buffer()
    ser.write(b"\x01")
    time.sleep(0.2)
    ser.reset_input_buffer()
    payload = code.encode() + b"\x04"
    for i in range(0, len(payload), 128):
        ser.write(payload[i:i + 128])
        time.sleep(0.02)
    buf = b""
    end = time.time() + timeout
    while time.time() < end:
        d = ser.read(256)
        if d:
            buf += d
            if b"\x04>" in buf:
                break
    return buf.decode("utf-8", "replace")


def main():
    print("PORT=%s PINS=%s HOLD=%.1fs CYCLES=%d" % (PORT, PINS, HOLD, CYCLES))
    print("表笔：黑->端口G，红->端口S。下面每条 STEP 就是一次电平变化。")
    print("-" * 60)
    ser = serial.Serial(PORT, BAUD, timeout=0.3)
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
    t0 = time.time()
    try:
        for c in range(CYCLES):
            print("=== 第 %d 轮 ===" % (c + 1))
            for n in PINS:
                t = time.strftime("%H:%M:%S", time.localtime())
                print("%s  GPIO%-3d HIGH  (t=%.1fs)" % (t, n, time.time() - t0))
                sys.stdout.flush()
                run_step(ser, STEP % (n, 1, int(HOLD * 1000), n, 1))
                t = time.strftime("%H:%M:%S", time.localtime())
                print("%s  GPIO%-3d LOW" % (t, n))
                sys.stdout.flush()
                run_step(ser, STEP % (n, 0, 400, n, 0))
    except KeyboardInterrupt:
        print("\n中断，正在把所有脚恢复为输入...")
    finally:
        for n in PINS:
            try:
                run_step(ser, "import machine\nmachine.Pin(%d, machine.Pin.IN)\nprint('RK')\n" % n, timeout=5.0)
            except Exception:
                pass
        ser.close()
        print("已复位为输入。测完记得把结果写进 docs/board_map.md。")


if __name__ == "__main__":
    main()
