# 固件 com13_20220808（第 1 代 · 量子兔 AlphaPi · ESP32-C3）

> **从实机 COM13 导出的板载文件（全量备份·21 文件）**。
> 配套文档：[`../../docs/AlphaPi_量子兔（COM13）分析报告.md`](<../../docs/AlphaPi_量子兔（COM13）分析报告.md>)。
>
> ⚠️ **这是第 1 代硬件**：ESP32-**C3** + 5×5 点阵 + N32 协处理器。
> 与第 2 代的 COM10 / COM11（ESP32-**S3** + ST7735 TFT）**完全不兼容**，
> 引脚、API、外设全部不同——参考 [`../README.md`](../README.md) 的代际表。

## 目录命名

`com13_20220808` = **串口号 + MicroPython 固件构建日期**（与 `com11_20220912` 同一约定）。
本机 `os.uname().version` 为 `v1.19.1-1-g71a8956f6-dirty on 2022-08-08`。

## 实机标识

| 项目 | 值 |
|---|---|
| 串口 | COM13，`VID_303A:PID_1001`（ESP32-C3 内置 USB-Serial/JTAG），USB 序列号 `68:67:25:EB:63:78` |
| Board 标识 | **`ESP32C3 module with ESP32C3`**（通用官方固件，非厂商定制） |
| MicroPython | `3.4.0; MicroPython v1.19.1-1-g71a8956f6-dirty on 2022-08-08` |
| 芯片 / 主频 | ESP32-C3 / 160 MHz |
| UID（=MAC） | `68:67:25:EB:63:78`（`machine.unique_id()` = `b'hg%\xebcx'`） |
| Flash | 4 MB；factory 分区 `addr 0x10000` / `size 2031616` |
| 文件系统 | 2 MB（已用 748 KB / 空闲 1.3 MB） |
| 主控模块 | `control_board_v1.mpy` → **`v_2020_7_31`** |
| basic 模块 | **`v_2020_7_31`** |
| 灯带 / 红外模块 | `v_2020_7_30` / `v_2020_7_30` |
| 显示 | **5×5 红色点阵 LED**（由 N32 协处理器的 UART 寄存器 `0x08` 驱动） |
| 连接要求 | **DTR 无关**（USB-Serial/JTAG，默认打开即可；无需 `--dtr`） |
| 备份时间 | **2026-09-26**（全量备份 21 文件） |

---

## `rootfs/` — 板载文件（全量 · 21 个 · 约 748 KB）

### 分类统计

| 类别 | 数量 | 文件 |
|---|---|---|
| 启动链 / 运行脚本（`.py`） | 3 | `boot.py` `main.py` `variable.py` |
| 编译模块（`.mpy`） | 4 | `control_board_v1.mpy` `basic.mpy` `actuator_led.mpy` `sensor_infrared.mpy` |
| 音频资源（`.dat`·IMA ADPCM） | 14 | `alert` `broken` `drop` `du` `electric` `funny` `msg` `pass` `r1` `record_end` `record_start` `right` `tech` `wrong` |

### 完整清单

| 文件 | 大小 | 类别 | 说明 |
|---|---:|---|---|
| `boot.py` | 139 | py | 官方默认模板（仅注释掉的 webrepl 代码），**无** `static_buf` |
| `main.py` | 1360 | py | **出厂程序**：人体红外触发 → WS2812 灯带点亮 + 播放 `r1.dat` |
| `variable.py` | 63 | py | `defaultVariable = DataStruct(0)` |
| `control_board_v1.mpy` | 8265 | mpy | **主控模块**（`v_2020_7_31`）：点阵 / 音频 / 按键 / 加速度 / GPIO / N32 UART 协议 |
| `basic.mpy` | 3154 | mpy | `DataStruct` 动态类型运行时（图形化编程基石） |
| `actuator_led.mpy` | 2309 | mpy | NeoPixel 灯带驱动（**14 颗**，`InitNP(pin)`） |
| `sensor_infrared.mpy` | 215 | mpy | 人体红外传感器（复用主控的 `pin_map`） |
| `alert.dat` | 20782 | 音频 | |
| `broken.dat` | 44974 | 音频 | |
| `drop.dat` | 27694 | 音频 | |
| `du.dat` | 16322 | 音频 | |
| `electric.dat` | 37486 | 音频 | |
| `funny.dat` | 26542 | 音频 | |
| `msg.dat` | 17686 | 音频 | |
| `pass.dat` | 18478 | 音频 | |
| **`r1.dat`** | **364544** | 音频 | **本代独有的大音频**（旧归档只有 53248 B） |
| `record_end.dat` | 17686 | 音频 | 录音结束提示音 |
| `record_start.dat` | 21428 | 音频 | 录音开始提示音 |
| `right.dat` | 20782 | 音频 | |
| `tech.dat` | 29422 | 音频 | |
| `wrong.dat` | 24812 | 音频 | |

---

## 与旧归档 `v2020_07_31/` 的关系（重要）

旧目录 `../v2020_07_31/` 来自原仓库（另一位研究者对自己那块 2020 版板子的取证）。
本次全量导出后逐文件 SHA256 比对，结论：

| 对比项 | 结果 |
|---|---|
| **4 个 `.mpy` 模块** | ✅ **逐字节完全一致** |
| 13 个 `.dat`（除 `r1.dat`） | ✅ 逐字节完全一致 |
| `boot.py` / `variable.py` | ✅ 逐字节完全一致 |
| **`main.py`** | ❌ 不同（本机 1360 B 出厂 Demo ／ 旧档 2047 B 另一版程序） |
| **`r1.dat`** | ❌ 不同（本机 364544 B ／ 旧档 53248 B） |
| `main2.py` / `test` | 仅存在于旧档，本机**没有** |

**两个直接结论**：

1. **反汇编请直接用 [`../v2020_07_31/disasm/`](../v2020_07_31/disasm/)**，本目录**不重复生成**。
   输入 `.mpy` 逐字节相同，反汇编天然等价（唯一差别是 `mpy-tool` 版本导致的
   `prelude:` 打印格式，与固件无关），重复存放只会产生"第二份真相"。
   API 全解见 [`../../docs/AlphaPi_项目分析文档.md`](<../../docs/AlphaPi_项目分析文档.md>) §5–§8。
2. 本机与旧档**是同代同版本固件、不同出厂程序**：本机是"红外→灯带+音乐"演示，
   旧档是另一版（含 `led_rect` / `led_array_demo` / Flash 恢复文件系统逻辑）。

---

## 硬件要点（实机实测）

| 项目 | 值 |
|---|---|
| **N32 协处理器** | `UART(1, 460800, tx=8, rx=9, timeout=100)` |
| **加速度计** | `SoftI2C(scl=7, sda=6, freq=400000)` → 从机 **`0x18`**（SC7A20 系，实测读数 `[-184, 80, -1064]`） |
| **按键 A / B / C** | GPIO **10 / 20 / 21**（`Pin.IN + PULL_DOWN`，按下为 1） |
| **人体红外** | GPIO **4**（`sensor_infrared.read_infrared_sensor(4)`） |
| **WS2812 灯带** | GPIO **5**，14 颗（`actuator_led.InitNP(5)`） |
| **5×5 点阵** | N32 寄存器 `0x08`；实测全亮、滚动显示 `HI` 均正常 |
| **麦克风 / 喇叭** | N32 `0x10`(录) / `0x11`(读 PCM) / `0x12`(读音量) / `0x14`(写音量) / `0x15`(播放流)；16 kHz·16 bit·单声道；半双工，单次录音 ≤20 s；实测音量 = 9 |
| **扩展口** | GPIO `3`（PWM 输出）、GPIO `4`/`5`（兼作 12864 LCD 子板 I2C，从机 `0x09`） |
| **pin_map 已缓存** | `{4, 20, 21, 10, 3}`（`ReadPin`/`ReadAdc`/`WritePin`/`WritePwm` 惰性建 Pin） |

> N32 寄存器表与音频参数见 [`../../docs/官方技术参考手册.md`](<../../docs/官方技术参考手册.md>)；
> N32 的 `0x90/0x80` 帧协议见 [`../v2020_07_31/README.md`](../v2020_07_31/README.md) §「N32 协处理器通信协议」。

### 固件内置能力（`help('modules')` 实测）

```
network   ubluetooth   usocket   ussl   ujson   ntptime   ure
webrepl   upip   neopixel   framebuf   dht   ds18x20   onewire   btree
```

- **WiFi 实测可用**：`STA_IF` 可激活，`scan()` 扫到 16 个热点 → 可做联网项目
- **BLE 可用**（`ubluetooth`）、**HTTPS/TLS** 可用（`ussl`）、**WebSocket** 可用（`uwebsocket`）
- 注意：无 `urequests`（可用 `upip` 装，或直接 `usocket` 手写 HTTP）

---

## 校验

逐文件 **SHA256 清单**见同目录 [`MANIFEST.md`](MANIFEST.md)（21 项，含大小与哈希，附复算命令）。

生成 / 复算：

```powershell
# 重新生成清单
python tools/_mkmanifest.py firmware/com13_20220808/rootfs firmware/com13_20220808/MANIFEST.md "2026-09-26 从实机 COM13 的这次全量备份"
```

## 备份 / 还原

```powershell
# 全量导出（本次即用此法；COM13 无需 --dtr）
python -m mpremote connect COM13 fs cp -r : firmware/com13_20220808/rootfs

# 全量还原
python -m mpremote connect COM13 fs cp -r firmware/com13_20220808/rootfs :

# 单个文件
python tools/repl_probe.py COM13 get main.py ./board_dump/com13/
python tools/repl_probe.py COM13 put main.py
python tools/repl_probe.py COM13 reset
```

> `repl_probe.py ... reset`（等价 `Ctrl-D`）会让板子重新执行 `boot.py` → `main.py`。
> **改完文件必须复位**，否则 `sys.modules` 里跑的还是旧代码。

## 快速验证

```powershell
python -m mpremote connect COM13 fs ls
python tools/repl_probe.py COM13 info
python tools/repl_probe.py COM13 run 'import control_board_v1 as c; print(c.version(), c.GetAccelerationRaw(), c.i2c.scan())'
```
