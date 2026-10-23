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
    return u.read(3)


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
    raw = b""
    for d in blocks:
        if not raw:
            raw = d
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
        print("%s: n=%d min=%d max=%d avg=%.1f std=%.1f raw=%s" % (
            name, n, mn, mx, avg, var ** 0.5, ubinascii.hexlify(raw).decode()))
    else:
        print(name, "NO_DATA")


def grab(rounds, gap=0.02):
    out = []
    for i in range(rounds):
        d = rd(0x11, 8)
        if len(d) > 1:
            out.append(d)
        time.sleep(gap)
    return out


print("=== BUZZER-MIC CROSS TEST ===")
w(0x10, b"\x01")
time.sleep(0.1)
stat("PRE", grab(10))
bm = cb.buzzerMission
bm.pwmPin.freq(2000)
during = []
for rep in range(4):
    bm.pwmPin.duty(512)
    during += grab(6, 0.04)
    bm.pwmPin.duty(0)
    during += grab(6, 0.04)
stat("DURING_BEEP", during)
stat("POST", grab(10))
w(0x10, b"\x00")
print("=== DONE ===")
