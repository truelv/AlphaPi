# 量子兔 AlphaPi（COM13）· 联网滚动时钟 —— 开机自启入口
#
# 出厂 Demo（红外 -> 灯带 + r1.dat）已备份在
# firmware/com13_20220808/rootfs/main.py，还原：
#   python tools/repl_probe.py COM13 put firmware/com13_20220808/rootfs/main.py main.py
#   python tools/repl_probe.py COM13 reset

import clock


clock.run()
