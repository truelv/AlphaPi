"""音频硬件自检：录音（你拍手）→ 自动分析麦克风 → 播放提示音（你听）。

一条命令搞定，节奏由你自己掌握：
    python tools/audio_selftest.py COM3

流程：
    1) 连接板子，音量拉到 100
    2) 录音 15 秒 —— 屏幕提示后请对着板子连续拍手 / 说话
    3) 自动把录音取回本机，逐秒分析能量：
          - 某秒 std>5 或 peak>30  → 麦克风真实拾到声音 → 【麦克风正常】
          - 全程 std<1             → 麦克风没有拾到声音（没拍 / 或麦克风异常）
    4) 播放出厂提示音 alert.dat（0x15 与 0x16 两条通路各一遍，音量 100）
          - 你听到声音             → 【喇叭正常】
          - 完全没声音             → 板上没有喇叭 / 喇叭未焊接 / 音频输出未接
    5) 结束自动软复位，小车主程序恢复运行

依赖: pip install pyserial
"""
import base64
import re
import sys
import time

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM3"
BAUD = 115200

REC_CODE = '''\
import controlBoardAlphaPiOne as cb
from basic import DataStruct
cb.set_volume(DataStruct(100))
cb.rec("selftest.dat", 15, False)
'''

PLAY_CODE = '''\
import controlBoardAlphaPiOne as cb
from basic import DataStruct
cb.set_volume(DataStruct(100))
cb.play("alert.dat", False)
cb.play("alert.dat", True)
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


def run_payload(ser, code, timeout=40.0):
    payload = code.encode() + b"\x04"
    for i in range(0, len(payload), 32):
        ser.write(payload[i:i + 32])
        time.sleep(0.01)
        deadline = time.time() + 0.3
        while time.time() < deadline:
            if ser.read(256):
                deadline = time.time() + 0.3
    buf = b""
    end = time.time() + timeout
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"\x04>" in buf:
                break
    return buf


def pull_file(ser, name, timeout=60.0):
    """分块 base64 导出板上文件，返回字节串。"""
    code = (
        "import os\n"
        "try:\n"
        "    print(os.stat(%r)[6])\n"
        "except Exception:\n"
        "    print(-1)\n" % name
    )
    out, _ = raw_exec(ser, code)
    try:
        size = int(out.strip().splitlines()[0])
    except Exception:
        return None
    if size < 0:
        return None
    data = b""
    offset = 0
    while offset < size:
        code = (
            "import ubinascii\n"
            "f = open(%r, 'rb')\n"
            "f.seek(%d)\n"
            "d = f.read(%d)\n"
            "f.close()\n"
            "print(ubinascii.b2a_base64(d).decode())\n" % (name, offset, min(512, size - offset))
        )
        out, _ = raw_exec(ser, code, timeout=15.0)
        text = out.decode("ascii", "ignore").strip()
        if not text:
            return None
        try:
            data += base64.b64decode(text)
        except Exception:
            return None
        offset += 512
        sys.stdout.write("\r  取回录音 %d/%d 字节" % (offset, size))
        sys.stdout.flush()
    print()
    return data


def raw_exec(ser, code, timeout=20.0):
    ser.write(b"\x03\x03")
    time.sleep(0.2)
    ser.reset_input_buffer()
    ser.write(b"\x01")
    time.sleep(0.3)
    ser.reset_input_buffer()
    payload = code.encode("utf-8") + b"\x04"
    for i in range(0, len(payload), 128):
        ser.write(payload[i:i + 128])
        time.sleep(0.03)
    buf = b""
    end = time.time() + timeout
    while time.time() < end:
        d = ser.read(1024)
        if d:
            buf += d
            if b"\x04>" in buf:
                break
    if buf.startswith(b"OK"):
        buf = buf[2:]
    if b"\x04" in buf:
        stdout, rest = buf.split(b"\x04", 1)
        stderr = rest.split(b"\x04")[0]
    else:
        stdout, stderr = buf, b""
    return stdout, stderr


def analyze(data):
    print("\n--- 麦克风逐秒能量（std=波动幅度，安静房间约 0.5）---")
    step = 24576  # 约 1 秒
    loud = []
    for i in range(0, len(data), step):
        seg = data[i:i + step]
        if len(seg) < 1000:
            break
        vals = [b - 128 for b in seg]
        n = len(vals)
        avg = sum(vals) / n
        std = (sum((v - avg) ** 2 for v in vals) / n) ** 0.5
        peak = max(abs(v) for v in vals)
        mark = ""
        if std > 5 or peak > 30:
            mark = "  <== 检测到声音！"
            loud.append(i // step)
        print("  第 %2d 秒: std=%7.2f peak=%3d%s" % (i // step, std, peak, mark))
    return loud


def main():
    print("PORT=%s" % PORT)
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2.0)
    ok = False
    for _ in range(6):
        if try_enter_raw(ser):
            ok = True
            break
        time.sleep(0.5)
    if not ok:
        print("连不上板子（串口被占用 / 板子没上电 / N32 卡死需拔插 USB）")
        ser.close()
        return

    print("\n=== 第 1 步：录音 15 秒 ===")
    print(">>> 请立即开始对着板子连续拍手 / 大声说话，持续 15 秒 <<<")
    run_payload(ser, REC_CODE, timeout=30.0)

    print("\n=== 第 2 步：取回录音并分析 ===")
    data = pull_file(ser, "selftest.dat")
    if data:
        loud = analyze(data)
        if loud:
            print("\n结论【麦克风】：正常 —— 第 %s 秒检测到明显声音" % loud)
        else:
            print("\n结论【麦克风】：15 秒内没有检测到任何声音。")
            print("  如果你确实拍手了 → 麦克风异常/未安装；如果没拍 → 重试本测试。")
    else:
        print("取回录音失败")

    print("\n=== 第 3 步：播放出厂提示音（音量 100，各通路一遍）===")
    print(">>> 请仔细听板子是否发出声音 <<<")
    run_payload(ser, PLAY_CODE, timeout=30.0)

    print("\n结论【喇叭】：你刚才听到声音了吗？")
    print("  听到了   → 喇叭正常")
    print("  没听到   → 板上没有喇叭 / 喇叭未焊接 / 音频输出电路未连接")

    # 收尾：删临时文件 + 软复位恢复小车主程序
    raw_exec(ser, "import os\ntry:\n    os.remove('selftest.dat')\nexcept Exception:\n    pass\n", timeout=8.0)
    ser.write(b"\x02")
    time.sleep(0.2)
    ser.reset_input_buffer()
    ser.write(b"\x04")
    time.sleep(2.0)
    ser.close()
    print("\n--- 已软复位，小车主程序恢复运行 ---")


if __name__ == "__main__":
    main()
