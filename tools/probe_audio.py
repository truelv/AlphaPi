"""音频硬件探针：实测板子的麦克风 / 喇叭（N32 音频协处理器，只读为主 + 极短提示音）。

原理（第 2 代 ESP32-S3，`controlBoardAlphaPiOne` 反汇编 + 实机验证）：
    N32 协处理器通过 UART(1, 460800/460929, tx=GPIO3, rx=GPIO0) 通信，帧协议：
        写帧 [0x90][addr][len][data...][cks]  -> 响应 [0x91][addr][cks]
        读帧 [0x80][addr][count]              -> 响应 [0x81][addr][len][data...][cks]
        cks = 除末字节外全部累加 & 0xFF
    音频寄存器：
        0x10 AUDIO_CTRL   写 1=开录音 0=停录（半双工，播前必须停录）
        0x11 AUDIO_READ   读麦克风 PCM（16kHz/16bit LE/mono）
        0x12              读音量（固件 read_volume() 实际读这里）
        0x14 VOLUME       写音量 0-100
        0x15 AUDIO_STREAM 写音频流播放，每块 200 字节 = 100 样本 = 6.25ms

用法:
    python tools/probe_audio.py COM3          # 默认：音量通路 + 麦克风采样 + 喇叭提示音
    python tools/probe_audio.py COM3 vol      # 只测音量通路（N32 音频子系统是否在线）
    python tools/probe_audio.py COM3 mic      # 只测麦克风（开录读 PCM 分析方差）
    python tools/probe_audio.py COM3 spk      # 只测喇叭（播 1kHz 方波约 0.5s，听声音）

探针结束后会自动退出 raw REPL 并软复位，板上原 main.py 随即恢复运行。

判读:
    - VOL=0~100 有回读        -> N32 音频编解码在线
    - MIC_ACTIVE               -> PCM 有明显波动（有麦克风且在采环境声）
    - MIC_SILENT               -> 读到的全是静音中点（无麦克风 / 被静音）
    - SPK_ACK 80/80            -> 播放通路全部应答（此时应能听到约 0.5s "哔"声）
"""
import os
import re
import sys
import time

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM3"
MODE = sys.argv[2] if len(sys.argv) > 2 else "all"
BAUD = 115200

# 板端执行的探针代码（raw REPL）
PAYLOAD = '''\
print("AUD_START")
import machine, time
import ubinascii
uart = machine.UART(1, 460800, tx=3, rx=0, txbuf=256, rxbuf=256, timeout=100)

def hx(b):
    return ubinascii.hexlify(bytes(b)).decode() if b else "None"

def cks(b):
    # 校验和 = 除末字节（校验字节自身）外全部累加；调用时传入的 b 尚未含校验字节
    s = 0
    for x in b:
        s += x
    return s & 0xFF

def w(addr, data):
    frame = bytearray([0x90, addr, len(data)]) + bytearray(data)
    frame.append(cks(frame))
    uart.read()
    uart.write(frame)
    return uart.read(3)

def rd(addr, count):
    # 响应分两段到达：3 字节头 [0x81][addr][len]，随后 len 数据 + 1 校验
    uart.read()
    uart.write(bytes([0x80, addr, count]))
    hdr = uart.read(3)
    if not hdr or len(hdr) < 3 or hdr[0] != 0x81:
        return b""
    data = uart.read(hdr[2] + 1)
    return bytes(data) if data else b""

# --- N32 音频通路在线检测：读音量寄存器 0x12 ---
resp = None
for _ in range(3):
    resp = rd(0x12, 1)
    if resp:
        break
    time.sleep(0.2)
if resp and len(resp) >= 1:
    print("VOL=%d" % resp[0])
else:
    print("VOL=ERR")

# --- 麦克风：开录音 -> 读 0x11 PCM（每次 8 字节，同固件）-> 增量统计 ---
import gc
gc.collect()
ack = w(0x10, b"\\x01")
print("REC_ON_ACK=%s" % hx(ack))
time.sleep(0.1)
n = 0; mn = 65536; mx = -65536; s = 0; sq = 0; raw = b""
for i in range(40):
    d = rd(0x11, 8)
    if d and len(d) >= 2:
        if not raw:
            raw = d
        for j in range(0, len(d) - 1, 2):
            v = d[j] | (d[j + 1] << 8)
            if v > 32767:
                v -= 65536
            if v < mn: mn = v
            if v > mx: mx = v
            s += v; sq += v * v; n += 1
ack = w(0x10, b"\\x00")
print("REC_OFF_ACK=%s" % hx(ack))
print("MIC_RAW=%s" % hx(raw[:32]))
if n:
    avg = s / n
    var = sq / n - avg * avg
    print("MIC n=%d min=%d max=%d avg=%.1f var=%.1f" % (n, mn, mx, avg, var))
    print("MIC_ACTIVE" if (mx - mn) >= 16 else "MIC_SILENT")
else:
    print("MIC_NO_DATA")

# --- 喇叭：音量 60，播约 500ms 1kHz 方波（连续"哔"，清晰可辨）---
ack = w(0x14, bytes([60]))
print("VOL_SET_ACK=%s" % hx(ack))
buf = bytearray()
for i in range(100):
    v = 12000 if (i // 8) % 2 == 0 else -12000
    buf.append(v & 0xFF)
    buf.append((v >> 8) & 0xFF)
ok = 0
for _ in range(80):
    a = w(0x15, buf)
    if a and len(a) == 3 and a[0] == 0x91 and a[2] != 0xFF:
        ok += 1
print("SPK_ACK %d/80" % ok)
print("AUD_END")
'''


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


def run_payload(ser, payload, timeout=40.0):
    code = payload.encode()
    i = 0
    while i < len(code):
        ser.write(code[i:i + 32])
        time.sleep(0.01)
        deadline = time.time() + 0.5
        while time.time() < deadline:
            d = ser.read(256)
            if d:
                deadline = time.time() + 0.5
        i += 32
    time.sleep(0.3)
    ser.reset_input_buffer()
    ser.write(b"\x04")
    buf = b""
    end = time.time() + timeout
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"AUD_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    starts = [m.start() for m in re.finditer("AUD_START", txt)]
    end_idx = txt.rfind("AUD_END")
    if starts and end_idx >= 0:
        return txt[starts[-1] + len("AUD_START"):end_idx].strip("\r\n ")
    if os.environ.get("AUD_DEBUG"):
        print("[debug raw]", repr(buf[-2000:]))
    return ""


def main():
    modes = {
        "vol": PAYLOAD.split("# --- 麦克风")[0] + 'print("AUD_END")\n',
        "mic": "print(\"AUD_START\")\n" + PAYLOAD.split("# --- N32 音频通路在线检测")[1].split("# --- 喇叭")[0] + 'print("AUD_END")\n',
        "spk": "print(\"AUD_START\")\n" + PAYLOAD.split("# --- 喇叭")[1],
        "all": PAYLOAD,
    }
    payload = modes.get(MODE, PAYLOAD)

    print("PORT=%s MODE=%s" % (PORT, MODE))
    print("-" * 60)
    print("注意：spk/all 模式会让板子喇叭发出约 0.5s 的 1kHz 提示音。")
    print("-" * 60)

    ser = serial.Serial(PORT, BAUD, timeout=0.5)
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

    out = run_payload(ser, payload)
    # 探针结束：退出 raw REPL 并软复位，让板子上原来的 main.py（如 remote_car）恢复运行
    ser.write(b"\x02")
    time.sleep(0.2)
    ser.reset_input_buffer()
    ser.write(b"\x04")
    buf = b""
    end = time.time() + 2.5
    while time.time() < end:
        d = ser.read(1024)
        if d:
            buf += d
            end = time.time() + 0.5
    ser.close()
    print(out if out else "(no output)")
    print("--- 已软复位，板子原程序已恢复运行 ---")


if __name__ == "__main__":
    main()
