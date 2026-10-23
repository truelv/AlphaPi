import time
import machine
import ubinascii
import controlBoardAlphaPiOne as cb
from basic import DataStruct

u = machine.UART(1, 460800, tx=3, rx=0, timeout=100)


def w(a, d):
    f = bytearray([0x90, a, len(d)]) + bytearray(d)
    s = 0
    for x in f:
        s += x
    f.append(s & 0xFF)
    u.read()
    u.write(f)
    r = u.read(3)
    if not r or len(r) != 3:
        time.sleep(0.05)
        u.read()
        u.write(f)
        r = u.read(3)
    return r


def rd(a, c):
    u.read()
    u.write(bytes([0x80, a, c]))
    h = u.read(3)
    if not h or len(h) < 3 or h[0] != 0x81:
        return b""
    return bytes(u.read(h[2] + 1))


def stat(name, blocks):
    n = 0
    mn = 99999
    mx = -99999
    s = 0
    sq = 0
    for d in blocks:
        for j in range(len(d)):
            v = d[j] - 128
            if v < mn:
                mn = v
            if v > mx:
                mx = v
            s += v
            sq += v * v
            n += 1
    if n:
        avg = s / n
        var = sq / n - avg * avg
        print("%s: n=%d min=%d max=%d avg=%.2f std=%.2f" % (name, n, mn, mx, avg, var ** 0.5))
    else:
        print(name, "NO_DATA")


def start_rec():
    r = w(0x10, b"\x01")
    time.sleep(0.1)
    rd(0x11, 8)  # 丢弃首个 filler 读
    return r


print("=== AUD PROBE 4 ===")
bm = cb.buzzerMission

print("T1: buzzer GPIO21 2kHz 1s (duty 700)")
start_rec()
blocks = []
bm.pwmPin.freq(2000)
bm.pwmPin.duty(700)
for i in range(45):
    d = rd(0x11, 8)
    if len(d) > 1:
        blocks.append(d)
    time.sleep(0.02)
bm.pwmPin.duty(0)
w(0x10, b"\x00")
stat("BUZZER_2kHz_1s", blocks)
time.sleep(0.5)

print("T2: vibration motor GPIO4 PWM 2kHz 1s")
vib = machine.PWM(machine.Pin(4), freq=2000, duty=0)
start_rec()
blocks = []
vib.duty(700)
for i in range(45):
    d = rd(0x11, 8)
    if len(d) > 1:
        blocks.append(d)
    time.sleep(0.02)
vib.duty(0)
vib.deinit()
w(0x10, b"\x00")
stat("VIB_GPIO4_2kHz_1s", blocks)
time.sleep(0.5)

print("T3: 0x15 playback while recording (fire-and-forget writes)")
start_rec()
blocks = []
f = open("alert.dat", "rb")
f.seek(44)
buf = bytearray(200)
nb = 0
while True:
    n = f.readinto(buf)
    if n <= 0:
        break
    fr = bytearray([0x90, 0x15, n]) + buf[:n]
    s = 0
    for x in fr:
        s += x
    fr.append(s & 0xFF)
    u.write(fr)
    nb += 1
    d = rd(0x11, 8)
    if len(d) > 1:
        blocks.append(d)
f.close()
w(0x10, b"\x00")
stat("DURING_0x15_PLAY", blocks)
print("blocks=%d" % nb)
print("=== DONE ===")
