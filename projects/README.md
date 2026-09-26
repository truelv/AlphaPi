# 项目

本目录存放**按项目分类**的完整工程，一个项目一个子目录，**每个项目自带文档**。
项目可以是"跑在板子上的应用"，也可以是"板端 + 上位机"的整套方案。

| 项目 | 目标 | 说明 |
|---|---|---|
| [`AlphaPiCar/`](AlphaPiCar/) | COM10 循迹小车 + PC/树莓派 | **网页遥控小车**：虚拟摇杆 / UDP 协议 / 电机+爪子+灯；含板端与上位机 |
| [`breakout/`](breakout/) | COM11 游戏机 | 打砖块游戏，摇杆控制挡板 |

## 项目目录约定

```
projects/<项目名>/
├── README.md        # 项目文档：架构 / 协议 / 用法 / 部署 / 排障
├── board/           # （如需要）烧到板子上的代码
├── host/            # （如需要）跑在 PC / 树莓派上的上位机
└── deploy/          # （如需要）部署资产：systemd 单元等
```

- 通用工具（串口 / REPL / 上传 / 反汇编 / 网页服务模板）放在 [`../tools/`](../tools/)。
- 板载 `main.py` 的开机自启与还原方法见各项目 README。

## 通用部署流程（板上项目示例）

```powershell
# 0) 先关掉 MobaXterm 等串口终端（串口独占）
python tools/repl_probe.py COM11 put projects/breakout/breakout.py game.py
python tools/repl_probe.py COM11 reset        # 必须复位，否则 sys.modules 里还是旧代码
```

> AlphaPiCar 的板端部署见 [`AlphaPiCar/README.md`](AlphaPiCar/README.md)。
