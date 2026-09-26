# 凭据模板 —— 复制成 clock_secrets.py 再填真实值
#
#   Copy-Item clock_secrets.example.py clock_secrets.py
#
# clock_secrets.py 已被 .gitignore 忽略（`*_secrets.py`），不会进仓库。
# 本文件（example）可以入库，**里面不要写真实密码**。
#
# 部署时两个文件都要传到板上：
#   python tools/repl_probe.py COM13 put projects/AlphaPiClock/board/clock_secrets.py clock_secrets.py

WIFI_SSID = "TP-LINK_XXXX"
WIFI_PASS = "your-wifi-password"
