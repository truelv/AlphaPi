# 固件 v2020_07_31（第 1 代，2020 版）

> **本目录是原仓库 `old/` 的内容**：某位研究者对自己那块 2020 版 AlphaPi 的完整取证。
> ⚠️ **它不适配第 2 代（2022-10 及以后）硬件**，仅作历史参考与逆向方法参考。

## 版本标识

| 项目 | 值 |
|---|---|
| 主控模块 | `control_board_v1.mpy` → `v_2020_7_31` |
| basic 模块 | `v_2020_7_31` |
| 灯带模块 | `actuator_led.mpy` → `v_2020_7_30` |
| 红外模块 | `sensor_infrared.mpy` → `v_2020_7_30` |
| 显示 | 5×5 红点阵 LED（经 N32 协处理器驱动） |
| MicroPython | 2023-07-14 |
| Flash | 4MB（dump 文件即 4MB） |

---

## `flash/`

| 文件 | 说明 |
|---|---|
| `AlphaPi_flash_4MB.bin` | 整片 4MB Flash 原始 dump，用 esptool 从板子读出 |

提取命令（原作者用法）：

```shell
~/Library/Arduino15/packages/esp32/tools/esptool_py/4.2.1/esptool \
  -p /dev/cu.usbmodem101 read_flash 0 0x400000 flash_contents.bin
```

分区信息：

```
>>> import esp32
>>> esp32.Partition.find()
[<Partition type=0, subtype=0, address=65536, size=2031616, label=factory, encrypted=0>]
```

---

## `rootfs/` — 板载文件系统

| 文件 | 说明 |
|---|---|
| `boot.py` | 空壳（只有被注释掉的 webrepl 代码） |
| `main.py` | 启动入口：检查文件数，不足则从 Flash `0x160000` 处的文件表恢复文件系统 |
| `main2.py` | `main.py` 的另一种版本 |
| `variable.py` | 全局变量容器 |
| `control_board_v1.mpy` | **主控板抽象层（8.07KB）**：LED / 音量 / 按键 / 录音播放 / 加速度 / GPIO |
| `basic.mpy` | `DataStruct` 动态类型运行时（3.08KB） |
| `actuator_led.mpy` | NeoPixel 灯带驱动（14 颗 WS2812） |
| `sensor_infrared.mpy` | 红外传感器 |
| `alert.dat` 等 13 个 `.dat` | 音频资源（IMA ADPCM）：alert / broken / drop / du / electric / funny / msg / pass / record_start / record_end / right / tech / wrong |
| `r1.dat` | 未解资源 |
| `test` | 出厂测试标记 |

---

## `disasm/` — 反汇编产物

| 文件 | 说明 |
|---|---|
| `control_board_v1.mpy.txt` | 主控模块反汇编（**131KB，核心分析材料**） |
| `basic.mpy.txt` | DataStruct 反汇编（52KB） |
| `actuator_led.mpy.txt` | 灯带模块反汇编（41KB） |
| `sensor_infrared.mpy.txt` | 红外模块反汇编（2.2KB） |
| `control_board_v1.mpy.freeze` 等 4 个 | 冻结字节码 |
| `control_board_v1.mpy.decompiled` | 尝试性反编译结果 |

重新生成：`python tools/mpy-tool.py -d <文件>.mpy > <文件>.mpy.txt`

---

## `examples/` — 配套示例

| 目录 | 说明 |
|---|---|
| `01_LED(OFFICAL METHODS)/` | 官方 5×5 点阵 API 用法（附效果图 `sample.png`） |
| `02_ACCEL/` | SC7A20 三轴加速度计直读（含 12 位补码转换） |
| `03_BUTTON/` | 按键封装类：`is_pressed` / `was_pressed` / `get_presses` / `irq` |
| `04_LED(WITH SOURCE CODE)/` | **手写 UART 协议驱动点阵——这套 N32 协议与第 2 代仍然通用** |

---

## `test/`

| 文件 | 说明 |
|---|---|
| `test.py` | 内容为 `../..//pycdc/test.py`，反编译调试残留 |
| `test.mpy` | 对应的编译产物 |

---

## API 速查（2020 版专用）

> 这些 API 只存在于第 1 代固件。第 2 代板子上没有 `control_board_v1`，只有
> `controlBoardAlphaPiOne`——详见 `../com10_20221028/README.md`。

### 5×5 点阵 LED

用 I2C 扩展芯片点亮 5×5 红色 LED，参数是 5 个数字的 `bytearray`（同步接口）：

```python
import control_board_v1

# 点亮最下面一行所有的灯
control_board_v1.led_show_bytes(bytearray([8, 8, 8, 8, 8]))
# 异步版本
control_board_v1.led_show_bytes_async(bytearray([9, 8, 0, 0, 0]))
```

位掩码对应关系：

| 参数 | 点亮位置 |
|---|---|
| `bytearray([8, 0, 0, 0, 0])` | 第 5 行第 1 列 |
| `bytearray([16, 0, 0, 0, 0])` | 第 4 行第 1 列 |
| `bytearray([128, 0, 0, 0, 0])` | 第 1 行第 1 列 |
| `bytearray([255, 255, 255, 255, 255])` | 全部点亮 |

### 类

- `control_board_v1.PlayRecordMission` —— 录音 / 播放任务状态机

### GPIO 对应（2020 版）

| 功能 | GPIO |
|---|---|
| button a / b / c | 10 / 20 / 21 |
| I2C（SC7A20 三轴） | SDA 6，SCL 7 |
| UART（N32 协处理器） | TX 8，RX 9，baudrate 460800 |
| P1 / P2 | 5 / 4（当年标注"未知"，后经手册确认为 I2C，用于 12864 LCD 子板） |

> 板上还有一个国产 N32 MCU，通过 UART 通信实现音频录制播放与 5×5 LED 功能。
> 原作者当年记录：「到此 alphapi 的硬件基本挖掘完毕」。

### N32 协处理器通信协议（与第 2 代通用）

```
写帧：[0x90][addr][len][data...][checksum]
      响应 [0x91][addr][checksum]
读帧：[0x80][addr][count]
      响应 [0x81][addr][len][data...][checksum]
校验和 = (0x90 + addr + len + data...) & 0xFF
```

`04_LED(WITH SOURCE CODE)` 示例里有一条实用的工程注释：

> 有时通信会卡死，原因未知，**连续写两次则必定成功**。

---

## 与第 2 代的差异（务必注意）

| 维度 | 本代（2020） | 第 2 代（2022-10 起） |
|---|---|---|
| 主控模块 | `control_board_v1` | `controlBoardAlphaPiOne` |
| 显示 | 5×5 点阵 LED | ST7735 TFT 160×128 |
| UART(TX/RX) | 8 / 9 @460800 | 3 / 0 @460929 |
| SPI | 无 | `sck41 / mosi42 / miso45` |
| I2C | SCL 7 / SDA 6 @400k | `scl9 / sda8` @100k（扩展口） |
| 中文字库 | 无 | HZK16 + gb2312 + sysfont |
| 网络 | 无 | WiFi 热点 / UDP 广播 |
