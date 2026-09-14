# 固件版本归档

本目录按**固件版本**存放 AlphaPi 各代固件的备份，**一个子目录 = 一代固件**。

## 版本一览

| 目录 | 代际 | 来源 | 显示 | 主控模块 | 状态 |
|---|---|---|---|---|---|
| `v2020_07_31/` | 第 1 代（2020） | 原仓库 `old/` | 5×5 点阵 LED | `control_board_v1` → `v_2020_7_31` | 历史资料 |
| `v1.0.3/` | 厂商迭代版 | 原仓库 `v1.0.3/` | — | `controlBoard` | 历史资料 |
| `com10_20221028/` | **第 2 代（2022-10 硬件）** | 实机 COM10 导出 | ST7735 TFT 160×128 | `controlBoardAlphaPiOne` → `v_2023_03_28` | **实机在用** |
| `com11_20220912/` | **第 2 代 · 手柄版** | 实机 COM11 全量导出 | ST7735 TFT 160×128 | 同上 | **实机在用** |

## 各版本目录内的统一结构

| 子目录 | 含义 | 出现在 |
|---|---|---|
| `rootfs/` | 板载文件系统的完整内容（`.py` 源码、`.mpy` 编译模块、`.dat` 音频、字库等） | 全部 |
| `disasm/` | 对 `.mpy` 反汇编得到的文本（由 `tools/mpy-tool.py` 生成） | 全部（`v1.0.3` 除外） |
| `flash/` | 整片 Flash 的原始 dump | 仅 `v2020_07_31` |
| `examples/` | 该版本配套的可运行示例 | 仅 `v2020_07_31` |
| `test/` | 反编译调试残留 | 仅 `v2020_07_31` |

## ⚠️ 代际不兼容警告

> **不要把 `v2020_07_31/flash/AlphaPi_flash_4MB.bin` 刷到第 2 代板子上。**
>
> 那是 2020 版硬件的固件：显示是 5×5 点阵（不是 TFT），UART / I2C / SPI 引脚全部不同。
> 刷进去基本等于变砖。第 1 代与第 2 代之间**没有兼容性**，仓库里的老 API 文档
> （如 `led_show_bytes`）在第 2 代板子上也不存在。

## 如何确认自己的板子属于哪一代

连上 REPL（`>`>>` 提示符）后执行：

```python
import os
print(os.uname())            # machine 字段 = Board 标识
import controlBoardAlphaPiOne as c
print(c.version())           # 主控模块版本
```

Board 标识对照：

| Board 标识 | 代际 |
|---|---|
| `AlphaPi One with ESP32S3` | 第 2 代**厂商定制**固件（COM10 那种） |
| `ESP32S3 module with ESP32S3` | 第 2 代**自编译通用**固件（COM11 那种） |

## 备份与还原

| 操作 | 命令 |
|---|---|
| 全量导出（推荐） | `python -m mpremote connect COM11 fs cp -r : ./firmware/com11_20220912/rootfs/` |
| 单个文件导出 | `python tools/repl_probe.py COM11 get boot.py ./x/` |
| 单个文件还原 | `python tools/repl_probe.py COM11 put boot.py` |
| 反汇编新模块 | `python tools/mpy-tool.py -d <文件>.mpy > <文件>.mpy.txt` |

详细的串口连接（DTR / 流控等）见 `docs/AlphaPi_实机调试指南.md`。
