# 固件版本归档

本目录按**固件版本**存放 AlphaPi 各代固件的备份，**一个子目录 = 一代固件**。

## 版本一览

| 目录 | 代际 | 来源 | 显示 | 主控模块 | 状态 |
|---|---|---|---|---|---|
| `v2020_07_31/` | 第 1 代（2020） | 原仓库 `old/` | 5×5 点阵 LED | `control_board_v1` → `v_2020_7_31` | 历史资料（含 4MB flash dump + examples + disasm） |
| **`com13_20220808/`** | **第 1 代** | **实机 COM13 全量导出** | **5×5 点阵 LED** | **`control_board_v1` → `v_2020_7_31`** | **实机在用** |
| `v1.0.3/` | 厂商迭代版 | 原仓库 `v1.0.3/` | — | `controlBoard` | 历史资料 |
| `com10_20221028/` | 第 2 代（2022-10 硬件） | 实机 COM10 全量导出 | ST7735 TFT 160×128 | `controlBoardAlphaPiOne` → `v_2023_03_28` | **实机在用** |
| `com11_20220912/` | 第 2 代 · 手柄版 | 实机 COM11 全量导出 | ST7735 TFT 160×128 | 同上 | **实机在用** |

> 子目录命名 = **串口号 + 该机 MicroPython 固件的构建日期**
> （例：`com13_20220808` ← `v1.19.1-1-g71a8956f6-dirty on 2022-08-08`）。

## 各版本目录内的统一结构

| 子目录 / 文件 | 含义 | 出现在 |
|---|---|---|
| `rootfs/` | 板载文件系统的完整内容（`.py` 源码、`.mpy` 编译模块、`.dat` 音频、字库等） | 全部 |
| `MANIFEST.md` | rootfs 逐文件 SHA256 校验清单（可由 `tools/_mkmanifest.py` 复算） | `com10` / `com11` / `com13` |
| `disasm/` | 对 `.mpy` 反汇编得到的文本（由 `tools/mpy-tool.py` 生成） | `v2020_07_31` / `com10` / `com11` |
| `flash/` | 整片 Flash 的原始 dump | 仅 `v2020_07_31` |
| `examples/` | 该版本配套的可运行示例 | 仅 `v2020_07_31` |
| `test/` | 反编译调试残留 | 仅 `v2020_07_31` |

> `com13_20220808/` **没有 `disasm/`**：它的 4 个 `.mpy` 与 `v2020_07_31/rootfs/` **逐字节一致**
> （见该目录 README 的比对表），反汇编直接复用 [`v2020_07_31/disasm/`](v2020_07_31/disasm/)，
> 避免在仓库里放"第二份真相"。

## ⚠️ 代际不兼容警告

> **第 1 代（ESP32-C3）与第 2 代（ESP32-S3）之间没有兼容性。**
> 显示器件（5×5 点阵 ↔ ST7735 TFT）、UART / I2C / SPI 引脚、主控模块 API
> （`control_board_v1` ↔ `controlBoardAlphaPiOne`）全部不同。
>
> **不要把 `v2020_07_31/flash/AlphaPi_flash_4MB.bin` 刷到第 2 代板子上**（会变砖），
> 也不要把第 2 代的 `controlBoardAlphaPiOne` 拿到第 1 代上 import（没有这个模块）。
> 仓库里的老 API 文档（如 `led_show_bytes`）**只适用于第 1 代**。

## 如何确认自己的板子属于哪一代

连上 REPL（`>>>` 提示符）后执行：

```python
import os
print(os.uname())            # machine 字段 = Board 标识
try:
    import control_board_v1 as c1      # 第 1 代
    print('GEN1', c1.version())
except ImportError:
    import controlBoardAlphaPiOne as c2  # 第 2 代
    print('GEN2', c2.version())
```

Board 标识对照：

| Board 标识 | 代际 |
|---|---|
| `ESP32C3 module with ESP32C3` | **第 1 代**（COM13 量子兔，5×5 点阵） |
| `AlphaPi One with ESP32S3` | 第 2 代**厂商定制**固件（COM10 那种） |
| `ESP32S3 module with ESP32S3` | 第 2 代**自编译通用**固件（COM11 那种） |

## 备份与还原

| 操作 | 命令 |
|---|---|
| 全量导出（推荐） | `python -m mpremote connect COM11 fs cp -r : ./firmware/com11_20220912/rootfs` |
| 单个文件导出 | `python tools/repl_probe.py COM11 get boot.py ./x/` |
| 单个文件还原 | `python tools/repl_probe.py COM11 put boot.py` |
| 生成校验清单 | `python tools/_mkmanifest.py <rootfs目录> <输出md> "备份说明"` |
| 反汇编新模块 | `python tools/mpy-tool.py -d <文件>.mpy > <文件>.mpy.txt` |

详细的串口连接（DTR / 流控等）见 `docs/AlphaPi_实机调试指南.md`。

## 相关文档

| 代际 | 实机分析报告 |
|---|---|
| 第 1 代（COM13 量子兔） | [`../docs/AlphaPi_量子兔（COM13）分析报告.md`](<../docs/AlphaPi_量子兔（COM13）分析报告.md>) |
| 第 2 代（COM10 循迹小车） | [`../docs/AlphaPi_循迹小车（COM10）分析报告.md`](<../docs/AlphaPi_循迹小车（COM10）分析报告.md>) |
| 第 2 代（COM11 游戏机） | [`../docs/AlphaPi_游戏机（COM11）分析报告.md`](<../docs/AlphaPi_游戏机（COM11）分析报告.md>) |
