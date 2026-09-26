<!-- check-links: off -->
<!-- 本文件部署到 /home/pi/Codes/README.md，下面的相对路径以"树莓派上的位置"为基准，
     在 Windows 仓库里检查会误报断链，故让 tools/check_links.py 跳过本文件。 -->

# /home/pi/Codes —— 项目代码仓库

本目录按**项目分类**存放树莓派上的代码，每个项目一个子目录，内含独立 `README.md`。
另有 `docs/` 存放**跨项目**的经验总结。

## 项目索引

| 项目 | 说明 | 入口 | systemd 服务 |
|---|---|---|---|
| [`AlphaPiCar`](./AlphaPiCar/) | AlphaPi-One 智能小车 · 网页遥控服务（HTTP + UDP） | `AlphaPiCar/car_web.py` | `alphaipi-web.service` |

## 文档

| 文档 | 说明 |
|---|---|
| [`docs/lessons_learned.md`](./docs/lessons_learned.md) | **踩坑与经验总结**（ESP32/MicroPython 逆向、串口、反编译、网络遥控、树莓派部署）——做新产品的避雷清单 |

## 目录约定

```
/home/pi/Codes/
├── README.md              # 本文件（项目 + 文档索引）
├── docs/                  # 跨项目文档
│   └── lessons_learned.md
└── <项目名>/
    ├── README.md          # 项目文档
    ├── *.py               # 代码
    └── systemd/
        └── *.service      # 服务单元（安装到 /etc/systemd/system/）
```

## 常用服务操作

```bash
sudo systemctl status  alphaipi-web     # 查看状态
sudo systemctl restart alphaipi-web     # 重启
sudo systemctl stop    alphaipi-web     # 停止
journalctl -u alphaipi-web -f           # 看日志
```
