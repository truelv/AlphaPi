import time
import machine
import controlBoardAlphaPiOne as cb
from basic import DataStruct

u = machine.UART(1, 460800, tx=3, rx=0, timeout=100)
LOG = open("clap_result.txt", "w")


def log(s):
    LOG.write(s + "\n")
    LOG.flush()


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


log("=== CLAP TEST: 12s continuous recording ===")
w(0x10, b"\x01")
time.sleep(0.1)
rd(0x11, 8)  # filler
samples = bytearray()
end = time.ticks_add(time.ticks_ms(), 12000)
while time.ticks_diff(end, time.ticks_ms()) > 0:
    d = rd(0x11, 8)
    if len(d) > 2:
        samples += d[:-1]
    time.sleep(0.005)
w(0x10, b"\x00")
log("total bytes: %d" % len(samples))
# 按 12288 B/s 约 1 秒一段，逐段统计
step = 12288
for i in range(0, len(samples), step):
    seg = samples[i:i + step]
    if len(seg) < 100:
        break
    n = len(seg)
    s = 0
    sq = 0
    mx = 0
    for b in seg:
        v = b - 128
        s += v
        sq += v * v
        if abs(v) > mx:
            mx = abs(v)
    avg = s / n
    std = (sq / n - avg * avg) ** 0.5
    log("sec %2d: n=%5d avg=%7.2f std=%7.2f peak=%d" % (i // step, n, avg, std, mx))
log("=== DONE ===")
LOG.close()
