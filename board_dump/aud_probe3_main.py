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


print("=== FIRMWARE REC REPRO ===")
print("vol:", rd(0x12, 3))
cb.rec("repro.dat", 2)
import os
print("repro.dat size:", os.stat("repro.dat")[6])
print("=== DONE ===")
