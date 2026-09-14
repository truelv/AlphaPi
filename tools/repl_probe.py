"""通过串口使用 MicroPython raw REPL，采集板子信息 / 导出板上的 .py 源码.

用法:
    python repl_probe.py COM10 info                     # 系统信息 + 文件列表 + 模块版本
    python repl_probe.py COM10 cat protocol.py          # 打印板上文件内容
    python repl_probe.py COM10 get protocol.py ./board/ # 分块导出到本地目录
    python repl_probe.py COM10 run "import os; print(os.listdir())" --dtr
    python repl_probe.py COM11 info           # 游戏机：DTR 已自动处理，无需 --dtr
    python repl_probe.py COM11 ls --dtr                  # 列出板上文件
    python repl_probe.py COM11 put ht_main.py --dtr      # 上传本地文件覆盖板上同名文件
    python repl_probe.py COM11 put ht_main.py game.py --dtr   # 另存为别的名字
    python repl_probe.py COM11 rm game.py --dtr          # 删除板上文件
    python repl_probe.py COM11 reset --dtr               # 软复位，让新代码生效

改代码的标准流程:
    1) get 把板上原文件导回本地做备份
    2) 本地改好 .py
    3) put 上传覆盖
    4) reset（或断电重启）重新执行 boot.py / main.py

原理: Ctrl-A 进入 raw REPL（不回显），发送代码 + Ctrl-D 执行，
      响应格式为 OK + stdout + \\x04 + stderr + \\x04> ，Ctrl-B 退出。
依赖: pip install pyserial
"""
import base64
import os
import sys
import time

import serial

INFO_CODE = '''import os, sys, gc
print("=== SYS ===")
print(sys.version)
print(sys.platform)
print("=== FILES ===")
fs = os.listdir()
print("count", len(fs))
for f in sorted(fs):
    try:
        print("%s|%d" % (f, os.stat(f)[6]))
    except Exception as e:
        print("%s|?" % f)
print("=== MEM ===")
gc.collect()
print("free=%d alloc=%d" % (gc.mem_free(), gc.mem_alloc()))
print("=== FLASH ===")
try:
    import esp
    print("flash_size", esp.flash_size())
except Exception as e:
    print("flash_err", e)
try:
    import esp32
    print("part", esp32.Partition.find())
except Exception as e:
    print("part_err", e)
print("=== MODULES ===")
for m in ["protocol", "protocal", "basic", "controlBoardAlphaPiOne", "ht_main",
          "static_buf", "sysfont", "ST7735", "machine_helper", "max30102", "variable"]:
    try:
        mod = __import__(m)
        v = getattr(mod, "version", None)
        print("%s|OK|%s" % (m, v() if v else ""))
    except Exception as e:
        print("%s|ERR|%s" % (m, e))
print("=== END ===")
'''


class Repl:
    def __init__(self, port, baud=115200, dtr=False):
        self.port = port
        self.baud = baud
        self.ser = serial.Serial(port, baud, timeout=0.2)  # 打开时 DTR 默认就是置位的
        self.dtr = True
        if dtr:
            self.ser.setDTR(True)
            self.ser.setRTS(False)
            return
        # 未显式传 --dtr 时自动判断：COM11 游戏机（ESP32-S3 原生 USB CDC）只有 DTR=1
        # 才把数据发给主机，而 DTR=1 正是打开端口的默认状态，所以这里不翻转即可。
        # 注意：DTR 在同一个句柄里翻转（先拉低再拉高）实测无法恢复通信，别那样做。
        # 若拿不到提示符，再拉低 DTR（部分电平转换芯片需 DTR=0 才不会自动复位）。
        if not self._probe(True):
            self.ser.setDTR(False)
            self.ser.setRTS(False)
            self.dtr = False
            print("[dtr] 收不到 REPL 提示符，已改为 DTR=0")

    def _probe(self, dtr):
        """发 Ctrl-C 看能否拿到友好 REPL 提示符."""
        try:
            self.ser.setDTR(dtr)
            self.ser.setRTS(False)
            time.sleep(0.2)
            self.ser.reset_input_buffer()
            self.ser.write(b"\x03\x03")
            time.sleep(0.5)
            return b">>>" in self.ser.read(4096)
        except Exception:
            return False

    def _read_until(self, token, timeout):
        buf = b""
        end = time.time() + timeout
        last = time.time()
        while time.time() < end:
            data = self.ser.read(1024)
            if data:
                buf += data
                last = time.time()
                if token in buf:
                    break
            elif buf and time.time() - last > 2.0:
                break
        return buf

    def raw_exec(self, code, timeout=15.0):
        """在 raw REPL 中执行代码，返回 (stdout, stderr) 字节串."""
        self.ser.write(b"\x03\x03")
        time.sleep(0.2)
        self.ser.reset_input_buffer()
        self.ser.write(b"\x01")
        time.sleep(0.3)
        self.ser.reset_input_buffer()
        payload = code.encode("utf-8") + b"\x04"
        # 分块发送：部分设备（尤其 USB CDC）接收缓冲仅 256 字节，整段发送会丢数据
        for i in range(0, len(payload), 128):
            self.ser.write(payload[i : i + 128])
            time.sleep(0.03)
        raw = self._read_until(b"\x04>", timeout)
        if raw.startswith(b"OK"):
            raw = raw[2:]
        if b"\x04" in raw:
            stdout, rest = raw.split(b"\x04", 1)
            stderr = rest.split(b"\x04")[0]
        else:
            stdout, stderr = raw, b""
        return stdout, stderr

    def close(self):
        try:
            self.ser.write(b"\x02")
        except Exception:
            pass
        try:
            self.ser.close()
        except Exception:
            pass


def cmd_info(repl):
    out, err = repl.raw_exec(INFO_CODE, timeout=30.0)
    sys.stdout.write(out.decode("utf-8", "replace"))
    if err.strip():
        sys.stdout.write("\n[stderr]\n" + err.decode("utf-8", "replace"))
    print()


def file_size(repl, name):
    code = (
        "import os\n"
        "try:\n"
        "    print(os.stat(%r)[6])\n"
        "except Exception as e:\n"
        "    print(-1)\n" % name
    )
    out, _ = repl.raw_exec(code, timeout=8.0)
    try:
        return int(out.strip().splitlines()[0])
    except (ValueError, IndexError):
        return -1


def read_chunk(repl, name, offset, length):
    code = (
        "import ubinascii\n"
        "f = open(%r, 'rb')\n"
        "f.seek(%d)\n"
        "d = f.read(%d)\n"
        "f.close()\n"
        "print(ubinascii.b2a_base64(d).decode())\n" % (name, offset, length)
    )
    out, err = repl.raw_exec(code, timeout=10.0)
    text = out.decode("ascii", "ignore").strip()
    if not text:
        return None
    try:
        return base64.b64decode(text)
    except Exception:
        return None


def dump_file(repl, name, out_dir, chunk=512):
    size = file_size(repl, name)
    if size < 0:
        print("SKIP %s: not found" % name)
        return False
    os.makedirs(out_dir, exist_ok=True)
    local = os.path.join(out_dir, os.path.basename(name))
    data = b""
    offset = 0
    while offset < size:
        block = read_chunk(repl, name, offset, min(chunk, size - offset))
        if not block:
            print("\nFAILED at offset %d" % offset)
            return False
        data += block
        offset += len(block)
        sys.stdout.write("\r  %s: %d/%d" % (os.path.basename(name), offset, size))
        sys.stdout.flush()
    with open(local, "wb") as fh:
        fh.write(data)
    print("\n  saved -> %s (%d bytes)" % (local, len(data)))
    return True


def write_chunk(repl, name, blob, first, timeout=20.0):
    """把一段原始字节以 base64 写入板载文件；first=True 时用 'wb' 截断重建."""
    mode = "wb" if first else "ab"
    b64 = base64.b64encode(blob).decode("ascii")
    # 按 120 字符切段 + 隐式拼接，避免出现超长单行（raw REPL 行长缓冲有限）
    pieces = [b64[i : i + 120] for i in range(0, len(b64), 120)] or [""]
    joined = "\n    ".join("b'%s'" % p for p in pieces)
    code = (
        "import ubinascii\n"
        "d = ubinascii.a2b_base64(\n    %s)\n"
        "f = open(%r, %r)\n"
        "f.write(d)\n"
        "f.close()\n"
        "print('WROTE', len(d))\n" % (joined, name, mode)
    )
    out, err = repl.raw_exec(code, timeout=timeout)
    if err.strip():
        sys.stdout.write("  [stderr] %s\n" % err.decode("utf-8", "replace"))
    return b"WROTE" in out


def cmd_put(repl, local, remote=None, chunk=512):
    """把本地文件分块写入板子（覆盖同名文件），写完自动校验长度."""
    remote = remote or os.path.basename(local)
    with open(local, "rb") as fh:
        data = fh.read()
    print("upload %s -> %s (%d bytes)" % (local, remote, len(data)))
    offset = 0
    first = True
    while first or offset < len(data):
        block = data[offset : offset + chunk]
        if not write_chunk(repl, remote, block, first):
            print("\nFAILED at offset %d" % offset)
            return False
        offset += len(block)
        first = False
        sys.stdout.write("\r  %d/%d" % (offset, len(data)))
        sys.stdout.flush()
    size = file_size(repl, remote)
    ok = size == len(data)
    print("\n  board size = %d -> %s" % (size, "VERIFY OK" if ok else "MISMATCH"))
    return ok


def cmd_ls(repl, path="."):
    code = (
        "import os\n"
        "for f in sorted(os.listdir(%r)):\n"
        "    try:\n"
        "        print('%%-28s %%8d' %% (f, os.stat(f)[6]))\n"
        "    except Exception:\n"
        "        print(f)\n" % path
    )
    out, _ = repl.raw_exec(code, timeout=10.0)
    sys.stdout.write(out.decode("utf-8", "replace"))


def cmd_rm(repl, name):
    code = (
        "import os\n"
        "try:\n"
        "    os.remove(%r)\n"
        "    print('removed')\n"
        "except Exception as e:\n"
        "    print('ERR', e)\n" % name
    )
    out, _ = repl.raw_exec(code, timeout=8.0)
    sys.stdout.write(out.decode("utf-8", "replace"))


def cmd_reset(repl, secs=2.5):
    """软复位（等价 Ctrl-D），让新写入的 boot.py / main.py 重新跑起来."""
    repl.ser.write(b"\x02")  # 退出 raw REPL
    time.sleep(0.2)
    repl.ser.reset_input_buffer()
    repl.ser.write(b"\x04")  # Ctrl-D -> 软复位
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        data = repl.ser.read(1024)
        if data:
            buf += data
            end = time.time() + 0.5
    sys.stdout.write(buf.decode("utf-8", "replace"))
    print("\n--- soft reset sent ---")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    port = sys.argv[1]
    action = sys.argv[2]
    dtr = "--dtr" in sys.argv
    repl = Repl(port, dtr=dtr)
    try:
        if action == "info":
            cmd_info(repl)
        elif action == "run":
            out, err = repl.raw_exec(sys.argv[3], timeout=20.0)
            sys.stdout.write(out.decode("utf-8", "replace"))
            if err.strip():
                sys.stdout.write("\n[stderr]\n" + err.decode("utf-8", "replace"))
        elif action == "cat":
            name = sys.argv[3]
            size = file_size(repl, name)
            print("size = %d" % size)
            offset = 0
            while 0 <= offset < size:
                block = read_chunk(repl, name, offset, 512)
                if not block:
                    break
                sys.stdout.write(block.decode("utf-8", "replace"))
                offset += len(block)
            print()
        elif action == "get":
            name = sys.argv[3]
            out_dir = sys.argv[4] if len(sys.argv) > 4 else "./board_dump/"
            dump_file(repl, name, out_dir)
        elif action == "put":
            local = sys.argv[3]
            remote = sys.argv[4] if len(sys.argv) > 4 else None
            cmd_put(repl, local, remote)
        elif action == "ls":
            cmd_ls(repl, sys.argv[3] if len(sys.argv) > 3 else ".")
        elif action == "rm":
            cmd_rm(repl, sys.argv[3])
        elif action == "reset":
            cmd_reset(repl)
        else:
            print("unknown action: %s" % action)
    finally:
        repl.close()


if __name__ == "__main__":
    main()
