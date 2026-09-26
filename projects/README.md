# 项目

本目录存放**按项目分类**的完整工程，一个项目一个子目录，**每个项目自带文档**。
项目可以是"跑在板子上的应用"，也可以是"板端 + 遥控端"的整套方案。

| 项目 | 目标硬件 | 说明 |
|---|---|---|
| [`AlphaPiClock/`](AlphaPiClock/) | **COM13 量子兔（第 1 代 ESP32-C3）** | **联网滚动时钟**：WiFi + NTP 对时 → 5×5 点阵滚动显示，按键切模式，灯带秒进度条 + 整点报时 |
| [`AlphaPiCar/`](AlphaPiCar/) | COM10 循迹小车 + PC/树莓派/手柄板 | **无线遥控小车**：两套遥控端（网页摇杆 / 手柄），UDP 协议，电机 + 夹爪 + 灯 |
| [`breakout/`](breakout/) | COM11 游戏机 | 打砖块游戏，摇杆控制挡板 |

## 项目目录约定

按「**被控端 / 遥控端**」分层：被控端只装一次，每种遥控方式各占一个子目录、自带 README 与部署脚本，**互不影响**。

```
projects/<项目名>/
├── README.md        # 项目文档：架构 / 协议 / 用法 / 部署 / 排障
├── board/           # （如需要）烧到"被控端/主设备"上的代码，只装一次
└── host/            # （如需要）遥控端
    └── <方式>/      #   每种遥控方式一个目录：代码 + README + 一键部署脚本
```

以 AlphaPiCar 为例：

```
AlphaPiCar/
├── board/                  # 小车端固件（两套遥控端共用）
└── host/
    ├── web/               # 网页版（PC / 树莓派），含 deploy/
    └── pad/               # 手柄版（手柄板固件），含 deploy_pad.py
```

- 通用工具（串口 / REPL / 上传 / 反汇编 / 文档链接检查）放在 [`../tools/`](../tools/)。
- 板载 `main.py` 的开机自启与还原方法见各项目 README。

## 通用部署流程（板上项目示例）

```powershell
# 0) 先关掉 MobaXterm 等串口终端（串口独占）
#    COM11 是 ESP32-S3 原生 USB CDC，务必加 --dtr（DTR=1/RTS=0）；
#    不加时工具的 DTR 自动探测可能误判并回退 DTR=0，会写坏板上文件。
python tools/repl_probe.py COM11 put projects/breakout/breakout.py game.py --dtr
python tools/repl_probe.py COM11 reset --dtr    # 必须复位，否则 sys.modules 里还是旧代码

# COM13 是 USB-Serial/JTAG，不需要 --dtr
python tools/repl_probe.py COM13 put projects/AlphaPiClock/board/clock.py clock.py
python tools/repl_probe.py COM13 put projects/AlphaPiClock/board/main.py  main.py
python tools/repl_probe.py COM13 reset
```

> ⚠️ **一台机器只有一块板**：下面这些项目会互相覆盖板载 `main.py`，要用哪个就先装哪个。
>
> | 板子 | 会互相覆盖的项目 |
> |---|---|
> | COM11（第 2 代 · 游戏机） | `breakout/`（打砖块） 与 `AlphaPiCar/host/pad/`（手柄遥控固件） |
> | COM13（第 1 代 · 量子兔） | `AlphaPiClock/`（时钟）—— 覆盖后出厂 Demo 需从 `firmware/com13_20220808/rootfs/main.py` 还原 |

## 相关文档

- AlphaPiCar：[`AlphaPiCar/README.md`](AlphaPiCar/README.md)（总览）·
  [`AlphaPiCar/host/README.md`](AlphaPiCar/host/README.md)（两套遥控端怎么选）
- breakout：[`breakout/README.md`](breakout/README.md)
- 工具：[`../tools/README.md`](../tools/README.md)
