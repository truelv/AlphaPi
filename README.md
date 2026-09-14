# AlphaPi 逆向研究与开发资料库

AlphaPi 是核桃编程（灵犀）生态的 ESP32-S3 教育开发板。本仓库是对该系列开发板的
**固件取证、API 还原与二次开发**资料库。

> ⚠️ **AlphaPi 存在多个互不兼容的硬件 / 固件代际。** 动手前请先确认手上的板子属于哪一代，
> 见 [`firmware/README.md`](firmware/README.md)。
> 把老固件刷到新板子上会导致设备不可用。

## 目录结构

```
AlphaPi/
├── firmware/          # 按固件版本归档（一个子目录 = 一代固件）
├── projects/          # 跑在板子上的应用 / 游戏（一个项目一个子目录）
├── tools/             # 串口、REPL、反汇编工具
├── docs/              # 分析文档（实机报告 + 调试指南）
└── reference/         # 官方技术参考手册
```

## 快速导航

| 我想…… | 看这里 |
|---|---|
| 确认手上的板子是哪一代 | [`firmware/README.md`](firmware/README.md) |
| 连上板子、进 REPL、看日志 | [`docs/AlphaPi_实机调试指南.md`](<docs/AlphaPi_实机调试指南.md>) |
| 了解循迹小车（COM10） | [`docs/AlphaPi_循迹小车（COM10）分析报告.md`](<docs/AlphaPi_循迹小车（COM10）分析报告.md>) |
| 了解游戏机（COM11） | [`docs/AlphaPi_游戏机（COM11）分析报告.md`](<docs/AlphaPi_游戏机（COM11）分析报告.md>) |
| 玩 / 改打砖块游戏 | [`projects/breakout/README.md`](projects/breakout/README.md) |
| 查 API 与硬件规格 | [`docs/AlphaPi_项目分析文档.md`](<docs/AlphaPi_项目分析文档.md>) + [`reference/`](reference/) |
| 用串口 / 反汇编工具 | [`tools/README.md`](tools/README.md) |

## 固件代际（重要）

| 代际 | 显示 | 主控模块 | 存放位置 |
|---|---|---|---|
| 第 1 代（2020） | 5×5 点阵 LED | `control_board_v1` | `firmware/v2020_07_31/` |
| 厂商迭代版 | — | `controlBoard` | `firmware/v1.0.3/` |
| **第 2 代（2022-10 起）** | ST7735 TFT 160×128 | `controlBoardAlphaPiOne` | `firmware/com10_20221028/`、`firmware/com11_20220912/` |

第 1 代与第 2 代**完全不兼容**：显示器件、UART、I2C、SPI 引脚全部不同，
API 也换了一整套（`control_board_v1` → `controlBoardAlphaPiOne`）。

> 仓库中的 `firmware/v2020_07_31/` 与 `firmware/v1.0.3/` 属于历史资料；
> 本仓库真正对应"手上这块板子"的是 `firmware/com10_20221028/` 和
> `firmware/com11_20220912/`，以及 `docs/` 下的两份实机分析报告。

## 快速上手

```powershell
pip install pyserial            # 必需

# 看板子在干什么（COM11 需要 DTR=1，脚本已自动处理）
python tools/serial_log.py COM11 115200 5
python tools/repl_probe.py COM11 ls
python tools/repl_probe.py COM11 run "import os; print(len(os.listdir()))"
```

串口连不上、界面全黑等问题的排查，见 [`docs/AlphaPi_实机调试指南.md`](<docs/AlphaPi_实机调试指南.md>)。

## 官方资料

- 官网：<http://lingxi.hetao101.com/alphapi>
- 技术参考手册：[`reference/AlphaPi_One_技术参考手册_v4.pdf`](<reference/AlphaPi_One_技术参考手册_v4.pdf>)

## 声明

本仓库内容来自对自有硬件的固件备份、逆向分析与公开资料整理，仅供学习研究使用。
