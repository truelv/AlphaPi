import time
import machine
import ubinascii
import controlBoardAlphaPiOne as cb
from basic import DataStruct

u = machine.UART(1, 460800, tx=3, rx=0, timeout=100)
LOG = open("aud_result.txt", "w")


def log(s):
    LOG.write(s + "\n")
    LOG.flush()
    print(s)


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
        for j in range(len(d) - 1):
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
        log("%s: n=%d min=%d max=%d avg=%.2f std=%.2f" % (name, n, mn, mx, avg, var ** 0.5))
    else:
        log("%s: NO_DATA" % name)


def rec_window(secs, label):
    w(0x10, b"\x01")
    time.sleep(0.1)
    rd(0x11, 8)  # filler
    blocks = []
    rounds = int(secs / 0.02)
    for i in range(rounds):
        d = rd(0x11, 8)
        if len(d) > 2:
            blocks.append(d[:-1])
        time.sleep(0.02)
    w(0x10, b"\x00")
    stat(label, blocks)
    return blocks


def play_file(path, reg):
    f = open(path, "rb")
    f.seek(44)
    buf = bytearray(200)
    nb = 0
    while True:
        n = f.readinto(buf)
        if n <= 0:
            break
        w(reg, buf[:n])
        nb += 1
    f.close()
    return nb


log("=== FINAL AUDIO TEST vol=100 ===")
log("P0 baseline 2s (quiet)")
rec_window(2.0, "P0_BASELINE")

log("P1 CLAP 3s")
rec_window(3.0, "P1_CLAP")

log("P2 buzzer GPIO21 2kHz 2s")
bm = cb.buzzerMission
w(0x10, b"\x01")
time.sleep(0.1)
rd(0x11, 8)
blocks = []
bm.pwmPin.freq(2000)
bm.pwmPin.duty(700)
for i in range(100):
    d = rd(0x11, 8)
    if len(d) > 2:
        blocks.append(d[:-1])
    time.sleep(0.02)
bm.pwmPin.duty(0)
w(0x10, b"\x00")
stat("P2_BUZZER", blocks)
time.sleep(0.3)

log("P3 alert.dat via 0x15 then immediate mic 1.5s")
nb = play_file("alert.dat", 0x15)
rec_window(1.5, "P3_AFTER_0x15")
log("  blocks=%d" % nb)
time.sleep(0.3)

log("P4 alert.dat via 0x16 then immediate mic 1.5s")
nb = play_file("alert.dat", 0x16)
rec_window(1.5, "P4_AFTER_0x16")
log("  blocks=%d" % nb)
log("=== DONE ===")
LOG.close()
