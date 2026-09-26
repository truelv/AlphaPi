"""一键把手柄固件烧到 ESP32-S3 手柄板（默认 COM11）。

用法:
    python projects/AlphaPiCar/host/pad/deploy_pad.py              # 默认 COM11
    python projects/AlphaPiCar/host/pad/deploy_pad.py COM11        # 指定串口
    python projects/AlphaPiCar/host/pad/deploy_pad.py --no-reset   # 只上传不复位

做三件事:
    1) 上传 remote_pad.py
    2) 上传 main_pad.py 另存为 main.py（开机自启）
    3) 软复位板子（让新代码生效）

注意:
    COM11 是 ESP32-S3 原生 USB CDC，**必须带 `--dtr`**（DTR=1 / RTS=0）。
    不带时 repl_probe 的 DTR 自动探测可能误判并回退到 DTR=0，
    导致上传失败、甚至把板上文件写坏。本脚本已强制加上。
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))                 # projects/AlphaPiCar/host/pad


def _find_repo_root(start):
    """向上找仓库根（含 tools/repl_probe.py 的那一层），比数 dirname 次数可靠。"""
    d = start
    for _ in range(8):
        cand = os.path.join(d, "tools", "repl_probe.py")
        if os.path.exists(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


REPL = _find_repo_root(HERE)


def main():
    args = sys.argv[1:]
    port = "COM11"
    for a in args:
        if not a.startswith("--"):
            port = a
    do_reset = "--no-reset" not in args

    if not REPL:
        print("找不到 tools/repl_probe.py（本脚本需要在仓库内运行）")
        sys.exit(1)

    def run(extra, must_contain):
        cmd = [sys.executable, REPL, port] + extra + ["--dtr"]
        print("$ " + " ".join(cmd))
        # 注意：不能用 text=True —— Windows 会用 GBK 解码子进程输出，
        # 而板子日志是 UTF-8 中文，会在 subprocess 的读取线程里抛 UnicodeDecodeError。
        proc = subprocess.run(cmd, capture_output=True)
        out = ((proc.stdout or b"").decode("utf-8", "replace")
               + (proc.stderr or b"").decode("utf-8", "replace"))
        print(out.rstrip())
        if must_contain not in out:
            print("!! 失败：输出里没有 %r（见上面的日志）" % must_contain)
            sys.exit(1)

    print("== 1/3 上传 remote_pad.py ==")
    run(["put", os.path.join(HERE, "remote_pad.py")], "VERIFY OK")

    print("== 2/3 上传 main.py（开机自启）==")
    run(["put", os.path.join(HERE, "main_pad.py"), "main.py"], "VERIFY OK")

    if do_reset:
        print("== 3/3 软复位 ==")
        cmd = [sys.executable, REPL, port, "reset", "--dtr"]
        print("$ " + " ".join(cmd))
        subprocess.run(cmd, capture_output=True)

    print("\ndone. 看日志：python tools/serial_log.py %s 115200 8 --no-ctrl-c" % port)


if __name__ == "__main__":
    main()
