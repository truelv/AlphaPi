# 固件 com10_20221028（第 2 代 · 循迹小车）

> **从实机 COM10 导出的板载文件**。配套文档：`docs/AlphaPi_循迹小车（COM10）分析报告.md`。

## 实机标识

| 项目 | 值 |
|---|---|
| 串口 | COM10，`VID_2F4E:PID_0102`（HETAO / N32 USB 桥接） |
| Board 标识 | **`AlphaPi One with ESP32S3`**（厂商定制固件） |
| MicroPython | `3.4.0; MicroPython 25d2a8a04 on 2022-09-30` |
| 出厂版本 | `SW_VER: 2022102803` / `HW_NAME: ONE \| Oct 28` |
| 主控模块 | `controlBoardAlphaPiOne.mpy` → `v_2023_03_28` |
| basic 模块 | `v_2022_11_30` |
| Flash | 8MB，factory 分区 addr `0x10000` / size 1376256 |
| 显示 | ST7735 TFT 160×128，SPI `sck41 / mosi42 / miso45`，`dc39 / rst38 / cs40` |
| 连接要求 | DTR 无关（与 COM11 不同） |
| 备份时间 | 2026-09-13 |

> ⚠️ **这是部分备份**，不是全量。只导出了明文源码与关键 `.mpy`（12 个文件）。
> 该板在采集后已离线，未能做完整导出。若要补全，请插上板子后执行：
> `python -m mpremote connect COM10 fs cp -r : ./firmware/com10_20221028/rootfs/`

---

## `rootfs/` — 板载文件

### 启动链

| 文件 | 大小 | 说明 |
|---|---|---|
| `boot.py` | 120B | 启动时读 N32 寄存器 `0x00`（按键状态），若 bit2/bit3 同时置位则 `import factory_reset`；随后分配 40KB `static_buf` |
| `main.py` | 43B | `import ht_main` + `ht_main.Start(static_buf)` |
| `ht_main.py` | 683B | **出厂程序**：开机 `sleep_ms(1000)` → `init()` → **开启 Wi-Fi 热点 `aiphapione` / `12345678`**，之后主循环空转 |

### 模块与数据

| 文件 | 大小 | 说明 |
|---|---|---|
| `controlBoardAlphaPiOne.mpy` | 22339B | **主控模块**：TFT 绘制 / 图层 Label / 图表 / 音频 / 网络广播 / 蜂鸣器 / GPIO |
| `basic.mpy` | 3393B | `DataStruct` 动态类型运行时（30 个方法） |
| `ST7735.mpy` | 8182B | 屏幕驱动（**坐标用元组**，见分析报告 §10.2） |
| `variable.py` | 63B | `defaultVariable = DataStruct(0)` |
| `music.py` | 25B | 占位函数 `def Update(): return`（主控模块导入时会自动重写） |
| `pen.py` | 25B | 同上 |
| `testok` | 2B | 内容 `ok`，出厂测试标记 |

---

## `disasm/` — 反汇编产物

| 文件 | 大小 | 说明 |
|---|---|---|
| `controlBoardAlphaPiOne.mpy.txt` | 391KB | 主控模块反汇编（**API 还原的主要依据**） |
| `ST7735.mpy.txt` | 157KB | 屏幕驱动反汇编（TFT 方法签名的来源） |
| `basic.mpy.txt` | 55KB | DataStruct 反汇编 |

---

## 硬件要点（实机实测）

| 项目 | 值 |
|---|---|
| UART（N32 协处理器） | `baudrate=460929, tx=3, rx=0, txbuf=256, rxbuf=256, timeout=100` |
| SPI（屏幕） | `id=2, baudrate=20MHz, sck=41, mosi=42, miso=45` |
| TFT 构造 | `TFT(spi, dc=39, reset=38, cs=40)` → `initr()` → `rgb(True)` → `fill(BLACK)` → `rotation(1)` |
| 扩展 I2C | `{'car': {'freq':100000, 'sda':8, 'scl':9}}` |
| 按键位掩码 | `keyP = [128, 64, 32, 16, 8, 4, 2, 1]` |
| 引脚对 | `PinPair = {1:{t:10,r:11}, 2:{t:12,r:13}, 3:{t:14,r:17}, 4:{t:18,r:48}}` |

---

## 快速验证

```powershell
python tools/repl_probe.py COM10 ls
python tools/repl_probe.py COM10 info
python tools/repl_probe.py COM10 run "import controlBoardAlphaPiOne as c; print(c.board_info())"
```
