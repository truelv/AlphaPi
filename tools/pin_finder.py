"""端口探针：靠"对地短接"把「P 端口 -> GPIO」映射表自动测出来。

原理：把候选 GPIO 全部设为 INPUT + PULL_UP，然后板端死循环盯着电平。
      你拿一根杜邦线一头接 GND，另一头去点端口的信号脚 —— 哪个 GPIO 被拉低，
      终端就实时打印 `#k  GPIO n -> LOW`。按 P1、P2、… 的顺序点，k 就是端口序号。

用法:
    python tools/pin_finder.py COM11            # 默认监听 240 秒
    python tools/pin_finder.py COM11 --sec 120
    python tools/pin_finder.py COM11 --pins 1,2,4,5

前置条件（重要）:
    1. USB 线插在**模块自己的 Type-C** 上（底板那个口只充电、不引 USB 数据）
    2. **底板断电**：拔掉底板 Type-C、开关拨到关 —— 这样端口 V 脚没有电压，
       随便点都不会短路。底板无源，信号线照样连通，不影响测试。
    3. 别碰 V 脚（电源脚），也别点模块的金手指那一排。

排除的脚（默认不动）:
    0? 保留（底板丝印出现过 0，值得测，上电后设输入无风险）
    19/20  USB D-/D+        26-32  Flash/PSRAM
    33-37  屏总线 / 电源使能  38-42  SPI 屏      43/44  UART0
"""
import re
import serial
import sys
import time

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM11"
BAUD = 115200

DEFAULT_PINS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21, 47, 48]
SEC = 240
if "--sec" in sys.argv:
    SEC = int(sys.argv[sys.argv.index("--sec") + 1])
# 给操作者留的准备时间：脚本先打印提示并倒数，倒数结束才开始监听
DELAY = 0
if "--delay" in sys.argv:
    DELAY = int(sys.argv[sys.argv.index("--delay") + 1])
PINS = DEFAULT_PINS
if "--pins" in sys.argv:
    PINS = [int(x) for x in sys.argv[sys.argv.index("--pins") + 1].split(",")]

PAYLOAD = """\
import machine, time
pins = %r
p = {}
for n in pins:
    try:
        p[n] = machine.Pin(n, machine.Pin.IN, machine.Pin.PULL_UP)
    except Exception:
        pass
ks = sorted(p.keys())
print("FIND_START")
last = {}
for n in ks:                      # 首轮只记录不打印，避免一堆 HIGH 噪声
    try:
        last[n] = p[n].value()
    except Exception:
        pass
n_low = 0
t0 = time.time()
while time.time() - t0 < %d:
    for n in ks:
        try:
            v = p[n].value()
        except Exception:
            continue
        if last.get(n) != v:
            last[n] = v
            if v == 0:
                n_low += 1
                print("#%%d  GPIO%%d -> LOW   (t=%%.1fs)" %% (n_low, n, time.time() - t0))
            else:
                print("    GPIO%%d 恢复 HIGH" %% n)
    time.sleep_ms(15)
for n in ks:
    try:
        machine.Pin(n, machine.Pin.IN)
    except Exception:
        pass
print("FIND_END")
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


def main():
    code = (PAYLOAD % (PINS, SEC)).encode()
    print("PORT=%s  监听 %d 秒  候选脚=%s" % (PORT, SEC, PINS))
    print("姿势：黑线一头接 GND，另一头按 P1→P2→… 依次点信号脚")
    if DELAY:
        print(">>> %d 秒后开始监听，请先把杜邦线准备好，接好 GND 那头 <<<" % DELAY)
        for i in range(DELAY, 0, -1):
            sys.stdout.write("\r    倒计时 %3d s " % i)
            sys.stdout.flush()
            time.sleep(1)
        print("\r>>> 开始！现在按 P1、P2、P3… 顺序点端口信号脚          ")
    print("-" * 64)
    ser = serial.Serial(PORT, BAUD, timeout=0.2)
    time.sleep(2.0)
    ok = False
    for _ in range(6):
        if try_enter_raw(ser):
            ok = True
            break
        time.sleep(0.5)
    if not ok:
        print("NO_RAW（串口被占用 / USB 没插模块？）")
        ser.close()
        return
    ser.reset_input_buffer()
    ser.write(b"\x01")
    time.sleep(0.2)
    for i in range(0, len(code), 128):
        ser.write(code[i:i + 128])
        time.sleep(0.02)
    ser.write(b"\x04")

    buf = b""
    end = time.time() + SEC + 20
    started = False
    while time.time() < end:
        d = ser.read(1024)
        if not d:
            if started and time.time() > end - 5:
                break
            continue
        buf += d
        txt = buf.decode("utf-8", "replace")
        if not started:
            if "FIND_START" in txt:
                started = True
                print("[板端已就绪] 开始监听电平变化…")
                idx = txt.find("FIND_START") + len("FIND_START")
                sys.stdout.write(txt[idx:].lstrip("\r\n"))
                sys.stdout.flush()
                buf = b""
            continue
        # 增量打印
        sys.stdout.write(txt)
        sys.stdout.flush()
        buf = b""
        if "FIND_END" in txt:
            break
    print()
    print("-" * 64)
    if not started:
        print("板端没有回 FIND_START —— 代码可能没跑起来。原始输出：")
        print(repr(buf[:800]))
    print("结束。把上面每条 `#k GPIO n` 按 k 的顺序对应 P1..P20，就是映射表。")
    ser.close()


if __name__ == "__main__":
    main()
