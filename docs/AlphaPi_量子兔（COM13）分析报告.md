# AlphaPi 量子兔（COM13）分析报告

> **设备归属**
> - **COM13 = 量子兔 AlphaPi（第 1 代）**｜`USB\VID_303A&PID_1001`（ESP32-C3 内置 USB-Serial/JTAG）｜Windows 显示「USB 串行设备」
> - COM10 = 循迹小车（第 2 代）｜`VID_2F4E:PID_0102`（HETAO/N32 桥接）→ [`AlphaPi_循迹小车（COM10）分析报告.md`](<AlphaPi_循迹小车（COM10）分析报告.md>)
> - COM11 = 游戏机（第 2 代）｜`VID_303A:PID_4001`（ESP32-S3 应用自定义 CDC）→ [`AlphaPi_游戏机（COM11）分析报告.md`](<AlphaPi_游戏机（COM11）分析报告.md>)
>
> 采集日期：**2026-09-26**（全量备份 + 实机探测）。
> 产物：`firmware/com13_20220808/`（全量 rootfs + SHA256 清单）、`board_dump/com13/`（探查中间产物）。

---

## 当前固件与运行状态

> 板上的固件和程序都可能被替换，**引用本文数据前请先核对这里**。
> 下表状态实测于 2026-09-26。

| 项目 | 值 | 来源 |
|---|---|---|
| MicroPython 内核 | **1.19.1** | `os.uname().release` |
| 编译来源 | **`v1.19.1-1-g71a8956f6-dirty on 2022-08-08`** | `os.uname().version` |
| Board 标识 | **`ESP32C3 module with ESP32C3`**（通用官方固件，**非**厂商定制） | `os.uname().machine` |
| 芯片 / 主频 | **ESP32-C3** / **160 MHz** | `machine.freq()` |
| UID（= MAC） | **`68:67:25:EB:63:78`** | `machine.unique_id()` |
| Flash | 4 MB；factory 分区 `addr 0x10000` / `size 2031616` | `esp.flash_size()` / `esp32.Partition.find()` |
| 文件系统 | 2 MB，已用 748 KB / 空闲 1.3 MB | `uos.statvfs('/')` |
| 内存 | free 96752 / alloc 27280 | `gc.mem_free()` / `mem_alloc()` |
| 板上文件总数 | **21** | `os.listdir()` |
| **开机自启程序** | `main.py`（1360 B）＝ **红外传感器 → 灯带点亮 + 播放 `r1.dat`** | 文件系统，见 §4.2 |
| 主控模块版本 | `control_board_v1` → **`v_2020_7_31`** | `control_board_v1.version()` |

**两个易混点**：

1. `sys.version` 开头的 `3.4.0` 是 **Python 语言版本**，不是 MicroPython 内核版本；
   内核版本要看 `os.uname().release`，本机为 **1.19.1**。
2. 名称里带 `dirty` 表示这份固件是**自行编译**的，但 `g71a8956f6` 是官方提交号且
   `machine` 标识为通用 `ESP32C3 module with ESP32C3` —— 即**基本是官方原版 MicroPython**，
   厂商只是往里放了几个 `.mpy` 库，没有改内核（与网上对该板的一致观察相符）。

---

## 1. 一句话结论

**COM13 是"量子兔 AlphaPi"的第 1 代硬件（ESP32-C3），与 COM10 / COM11 的第 2 代（ESP32-S3）
不是同一代产品**：显示从 5×5 点阵换成 ST7735 TFT，主控模块从 `control_board_v1`
换成 `controlBoardAlphaPiOne`，引脚与 API 全换。

它的能力构成：

- **双 MCU**：ESP32-C3 当大脑，国产 **N32** 通过 UART 承担 *音频编解码 + 5×5 点阵 + 按键扫描*
- **板载外设**：5×5 红色点阵 LED、麦克风 + 喇叭、三轴加速度计（SC7A20 系）、3 个按键、
  人体红外接口、**14 颗 WS2812 RGB 灯带**、GPIO 扩展口
- **关键点（最容易被低估）：固件内置 `network` / `ubluetooth` / `ussl` / `uwebsocket`，
  而且 WiFi 实测能扫到 16 个热点**——所以它不只是"点灯玩具"，**可以联网**做真作品

---

## 2. 设备识别

| 项目 | 值 | 对比：COM10 / COM11（第 2 代） |
|---|---|---|
| 串口 | COM13 | COM10 / COM11 |
| USB | `VID_303A:PID_1001`，ESP32-C3 内置 USB-Serial/JTAG，序列号 `68:67:25:EB:63:78` | `2F4E:0102`（N32 桥接）/ `303A:4001`（应用自定义 CDC） |
| **DTR / RTS** | **无关**，默认打开即可（见 §3） | COM11 **必须 DTR=1 且 RTS=0**；COM10 无关 |
| MicroPython | `3.4.0; v1.19.1-1-g71a8956f6-dirty on 2022-08-08` | `25d2a8a04 on 2022-09-30` / `8e2a5ed99-dirty on 2022-09-12` |
| build 标识 | **`ESP32C3 module with ESP32C3`** | `AlphaPi One with ESP32S3` / `ESP32S3 module with ESP32S3` |
| 主频 | **160 MHz**（ESP32-C3 上限） | 240 MHz（双核） |
| Flash | 4 MB，factory `size 2031616` | 8 MB |
| 文件数 | **21** | 62 / 74 |
| 内存 | free 96752 / alloc 27280 | free 48528 / 57152 |
| 显示 | **5×5 红点阵**（经 N32） | ST7735 TFT 160×128（SPI） |
| 主控模块 | **`control_board_v1`** → `v_2020_7_31` | `controlBoardAlphaPiOne` → `v_2023_03_28` |

> esptool / `mpremote` 均可连（`PID_1001` 是 ROM 内置的 USB-Serial/JTAG，
> 与 COM11 那个拿不到 ROM bootloader 的自定义 CDC **不同**）。

---

## 3. 连接方式（与 COM11 的关键区别）

COM13 是 **ESP32-C3 的 USB-Serial/JTAG**，行为比 COM11 那种 TinyUSB CDC 温和得多：

| 项目 | COM13 |
|---|---|
| 波特率 | 实际由 USB 决定，填 `115200` 与否都能通 |
| 流控 | `None` |
| DTR / RTS | **不用管**（`tools/repl_probe.py COM13 ...` **不需要** `--dtr`） |
| 打开串口 | 会**打断**当前程序（等价的"一连就停"），`Ctrl-C` 出 `>>>` |

```powershell
python tools/serial_log.py COM13 115200 6          # 看启动日志 / 打断当前程序
python tools/repl_probe.py COM13 info              # 系统信息 + 文件清单 + 模块版本
python -m mpremote connect COM13 fs ls             # 列文件（官方工具，更快）
python -m mpremote connect COM13 fs cp -r : ./firmware/com13_20220808/rootfs   # 全量备份
```

> ⚠️ `mpremote ... fs cp -r : <目标目录>` 要求**目标目录已存在**，否则报
> `cp: : Operation not permitted`。先 `New-Item -ItemType Directory -Force` 建好再导。

终端按键、shell 命令对照、`Ctrl-E` 粘贴模式、传文件流程见
[`AlphaPi_实机调试指南.md`](<AlphaPi_实机调试指南.md>)（三块板通用）。

---

## 4. 启动链

### 4.1 `boot.py`（139 B）

```python
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
```

= **官方 MicroPython 的默认 `boot.py` 模板，原封未动**：没有 `static_buf`、没有按键检测、
没有工厂复位逻辑。**这与第 2 代两块板都不一样**（COM10 的 `boot.py` 有 N32 按键检测 +
`import factory_reset`，COM11 的有 40 KB `static_buf`）。

> 这直接意味着：**这块板子没有"按住某键开机自动恢复出厂"的机制**，改坏了直接
> `mpremote fs cp -r` 把 `firmware/com13_20220808/rootfs/` 灌回去即可。

### 4.2 `main.py`（1360 B）—— 出厂 Demo

完整源码（与本机逐字节一致，已存档到 `firmware/com13_20220808/rootfs/main.py`）：

```python
import control_board_v1
import actuator_led
import sensor_infrared
import variable
import time
import math
import basic
from basic import DataStruct
from basic import wait_time


control_board_v1.led_show_bytes(bytearray([0x00, 0x00, 0x00, 0x00, 0x00]))
soundLoop = control_board_v1.play_record_loop()


def Loop1():
    actuator_led.InitNP(5)
    while True:
        if (((DataStruct(sensor_infrared.read_infrared_sensor(4))) == (DataStruct("1")))).BoolValue():
            actuator_led.setPixelColor((DataStruct(1)) - 1, DataStruct(16777215))
            actuator_led.setPixelColor((DataStruct(13)) - 1, DataStruct(16777215))
            actuator_led.setPixelColor((DataStruct(14)) - 1, DataStruct(16777215))
            actuator_led.setPixelColor((DataStruct(7)) - 1, DataStruct(16777215))
            play_loop = control_board_v1.playUntilDone("r1.dat")
            play_loop_has_next = True
            while (play_loop_has_next):
                play_loop_has_next = next(play_loop)
                yield True
            yield True
        else:
            actuator_led.setPixelColor((DataStruct(15)) - 1 , DataStruct(0))
            yield True
        yield True
    yield False


loop1 = Loop1()
loop1HasNext = True


while True:
    control_board_v1.UpdateButtonStatus()
    next(soundLoop)
    if loop1HasNext:
        loop1HasNext = next(loop1)
```

**逻辑**：`GPIO4` 上的人体红外读到 `1`（有人）→ 点亮灯带第 1/13/14/8 颗 → 播放 `r1.dat`；
否则熄灭第 15 颗。

**这就是本站 `Ctrl-C` 打断时看到的 `main.py, line 45, in <module>`**
（第 45 行 `loop1HasNext = next(loop1)`）——恰好卡在等 `r1.dat` 播完。

**三个可直接复用的惯用法**：

1. **生成器协作式调度**：`play_record_loop()` / `playUntilDone()` / `wait_time()` 都是 `yield`
   生成器，主循环每帧 `next(...)` 一次 —— 这就是"图形化积木运行时"的真身，
   **异步不阻塞**（见 [`AlphaPi_项目分析文档.md`](AlphaPi_项目分析文档.md) §4.2）。
2. **音频主循环泵必须每帧喂**：`next(soundLoop)` 一旦停掉，录音/播放就全停。
3. **`DataStruct` 是硬约束**：`actuator_led.setPixelColor` 的参数必须包成 `DataStruct`，
   否则底层按动态类型取值会失败。`(DataStruct(13)) - 1` 就是"第 12 号灯珠"。

> 本机与旧归档 `firmware/v2020_07_31/rootfs/main.py`（2047 B）**不是同一份程序**：
> 旧档那版含 `led_rect` / `led_array_demo` / 从裸 Flash 恢复文件系统的 `get_files_from_flash()`。

---

## 5. 硬件清单（实机实测）

### 5.1 总线与器件

| 部件 | 接口 / 引脚 | 实测结果 |
|---|---|---|
| **N32 协处理器** | `UART(1, 460800, tx=8, rx=9, timeout=100)` | 在线（音量读回 `9`） |
| **三轴加速度计** | `SoftI2C(scl=7, sda=6, freq=400000)` → 从机 **`0x18`** | ✅ 读数 `[-184, 80, -1064]` |
| **按键 A / B / C** | GPIO **10 / 20 / 21**（`Pin.IN + PULL_DOWN`，按下为 1） | `0 / 0 / 0`（未按） |
| **人体红外** | GPIO **4** | 读到 `0` |
| **WS2812 灯带** | GPIO **5**，**14 颗** | 出厂 Demo 正在驱动 |
| **5×5 红点阵** | N32 寄存器 `0x08` | ✅ 实测全亮 OK、滚动显示 `HI` OK |
| **麦克风 / 喇叭** | N32 `0x10` / `0x11` / `0x12` / `0x14` / `0x15` | 16 kHz·16 bit·单声道，半双工 |
| **扩展口** | GPIO `3`（PWM）、GPIO `4` / `5` | 与 12864 LCD 子板 I2C 复用（从机 `0x09`） |

> **I2C 总线只有加速度计一个从机**：`SoftI2C(7, 6).scan()` → `['0x18']`。
> 固件按扫到的地址分支初始化为 `0x12` 或 `0x18` 两种加速度计批次
> （本机命中 `0x18` 分支）。
>
> `pin_map` 惰性缓存表实测已含 `{3, 4, 10, 20, 21}`。

### 5.2 N32 协处理器寄存器表（官方手册 §6.4）

| 地址 | 名称 | 读写 | 说明 |
|---|---|---|---|
| `0x00` | KEY | 读 | 按键状态，A 键 = bit2（`0x04`） |
| `0x08` | — | 写 | **5×5 点阵**：变长列点阵字节流，**写入长度决定 N32 滚不滚**（见 §5.4） |
| `0x10` | AUDIO_CTRL | 写 | 录音控制：1 = 开，0 = 关 |
| `0x11` | AUDIO_READ | 读 | 读取麦克风 PCM |
| `0x12` | — | 读 | `read_volume()` 实际读的地址 |
| `0x14` | VOLUME | 写 | 音量 0–100 |
| `0x15` | AUDIO_STREAM | 写 | 音频流写入（播放），**每块 200 字节** |

**帧协议**（第 1、2 代通用）：

```
写帧  [0x90][addr][len][data...][checksum]   响应 [0x91][addr][checksum]
读帧  [0x80][addr][count]                    响应 [0x81][addr][len][data...][checksum]
checksum = (0x90 + addr + len + data...) & 0xFF        # 除末字节外全部累加
```

> 官方示例里有条实用注释：**N32 通信偶发卡死，原因未知，「连续写两次则必定成功」**。
> 自己写驱动时建议加"失败重试 + 双写"。

### 5.3 音频参数

- 格式：**16 kHz / 16-bit signed little-endian / 单声道 PCM**
- 每块 200 字节 = 100 样本 = 6.25 ms
- **半双工：播放前必须先停录**（写 `0x10 = 0`）
- 单次录音最长 **20 秒**（固件里 `sec` 被硬钳制）
- 出厂音频 14 个 `.dat`（IMA ADPCM）：`alert` `broken` `drop` `du` `electric` `funny`
  `msg` `pass` `r1` `record_end` `record_start` `right` `tech` `wrong`
  （其中 `r1.dat` **364544 B**，是本代独有的大音频）

### 5.4 寄存器 `0x08`：写入长度决定「静态」还是「滚动」（重要）

点阵**不是固定 5 列的静态屏**，而是"5 列视窗 + 变长缓冲"的滚动条。N32 的行为只看**写入字节数**：

| 写入长度 | N32 行为 | 耗时规律 |
|---|---|---|
| **= 5**（正好一屏宽） | **静态显示**，不滚动 | `led_show_bytes()` 固定 `sleep_ms(400)` |
| **> 5** | 横向滚动，滚一列约 **100 ms** | `led_show_string()` 按 `sleep_ms((len-5)*100 + 400)` 等待 |

推论（都已在实机验证）：

- **同步接口的阻塞时间正比于内容长度**：`led_show_string("12:34")`（约 29 字节）要阻塞 **3～4 秒**，
  主循环会被卡死。**必须用 `_async` 版本**，自己控制重刷节奏。
- **一屏静态信息量 = 5 列**。固件自带 `charPointMap` 里**每个字符就是 5 字节 = 5 列**，
  即"**一个字符占满整屏**"，所以 `12:34` 这类内容必然要滚。
- ⚠️ **"自制窄体字模"这条路实测走不通**（2026-09-26 在 COM13 上做完后回退）：
  2 列 × 5 行虽然能凑出「2 位数字 + 1 列间隔 = 5 列」，但 **10 个像素要区分 10 个数字**，
  两两平均只差 1～2 像素（`1`/`7`、`0`/`8` 只差 1 个像素），**真机上比原生 5×5 大字难认得多**；
  而且一屏仍只放得下 2 位，时间还得"时/分"交替，一次照样看不全。
  → **结论：这块屏上「滚动」就是最优解**，不必再往"静态窄体字"方向投入。
- 要做静态只能用**原生 5×5 单字**（一屏一位），但一屏一位（每位约 1.2 秒）比滚动更慢，也没意义。
- 补充踩坑：**不能照搬七段数码管**。2 列下每个段只有 1 像素，`1` 的竖笔画会变成
  R1/R3 两个孤立点（虚线），必须按 2×5 像素**手工画**字形。

**列点阵位序**（`bytearray` 一字节 = 一列，高位在上）：

| 行（自上而下） | 位 |
|---|---|
| 第 1 行（顶） | `0x80` |
| 第 2 行 | `0x40` |
| 第 3 行 | `0x20` |
| 第 4 行 | `0x10` |
| 第 5 行（底） | `0x08` |

可用固件常量直接取字模：`control_board_v1.charPointMap[ch]` → `bytearray(5)`，
缺字兜底 `defaultCharPointMap`（全 `0x00`）。

---

## 6. 模块 API 参考（第 1 代专用）

> 完整逐函数分析见 [`AlphaPi_项目分析文档.md`](AlphaPi_项目分析文档.md) **§5–§8**
> （含反汇编依据）。本节只给"上手要用的最小集"。

### 6.1 `control_board_v1`（`v_2020_7_31`）

```python
import control_board_v1 as cb

# —— 5×5 点阵 ——
cb.led_show_bytes(bytearray([255,255,255,255,255]))   # 全亮（阻塞等待滚动完成）
cb.led_show_bytes_async(bytearray([128,0,0,0,0]))     # 左上角一颗，不阻塞
cb.led_show_string("HI")                              # 94 字符 ASCII 字模，N32 自动滚动
cb.led_show_string_async("12:34")                     # 同上但不阻塞（时钟就靠它）

# —— 加速度 ——
x, y, z = cb.GetAccelerationRaw()
cb.GetAcceleration(3)                                 # 合加速度；0/1/2 = 各轴
cb.IsForward(5)                                       # 6 向姿态判定
cb.CheckForward((x,y,z), 0, 0, 900, 300)              # 是否处于中位

# —— 按键 ——
cb.UpdateButtonStatus()                               # 刷新 pa/pb/pc_last_status（每帧都要调）
cb.GetLastPinStatus(10)                               # A 键状态

# —— GPIO / ADC / PWM ——
cb.WritePin(3, 1); cb.WritePwm(3, 512); v = cb.ReadAdc(3)   # ReadAdc 返回 10 位

# —— 音频（必须每帧 next(soundLoop)）——
soundLoop = cb.play_record_loop()
cb.play('alert.dat')                                  # 阻塞播放
cb.playAsync('msg.dat')                               # 异步播放
cb.rec('my.dat', 5)                                   # 阻塞录音 5 秒
cb.read_volume()                                      # 读音量

# —— 生成器（图形化积木语义）——
cb.voidCommand(); cb.Clamp(v, 0, 1023); cb.average([1,2,3]); cb.GetSysTime()
```

> 点阵字模是 **94 项 ASCII**（`0-9 a-z A-Z` + 常见符号），**没有中文**。
> 想显示中文得自己做字模，或用 N32 的 `0x08` 直接写 5 字节列点阵。

### 6.2 `actuator_led`（`v_2020_7_30`）—— WS2812 灯带

```python
import actuator_led as al
from basic import DataStruct

al.InitNP(5)                                  # 参数是 GPIO，不是灯珠数！固定 14 颗
al.SetBrightness(DataStruct(50))              # 0–100（注意必须包 DataStruct）
al.setPixelColor(DataStruct(0), DataStruct(16777215))   # 索引, 打包后的 RGB
al.ShowRainbow()                              # 彩虹循环
al.pixelShowU(DataStruct(v), DataStruct(255)) # 音量条效果（绿→黄→橙→红）
al.SetBrightness / BrightnessUp / UpdateBrightness / GetBrightness
```

> ⚠️ 与第 2 代同样的坑：`SetBrightness()` 只把亮度**乘到已有颜色**上，
> 首次要亮必须先 `setPixelColor()` 设颜色，否则"黑 × 亮 = 黑"。

### 6.3 其它

| 模块 | 版本 | 作用 |
|---|---|---|
| `basic`（`v_2020_7_31`） | — | `DataStruct` 动态类型运行时 + `wait_time` 生成器 + `data_struct_normalization` 线性映射 |
| `sensor_infrared`（`v_2020_7_30`） | — | `read_infrared_sensor(pin_port)`，**跨模块复用 `control_board_v1.pin_map`** |
| `variable` | — | `defaultVariable = DataStruct(0)` |

### 6.4 固件内置模块（`help('modules')` 实测裁剪）

```
network   ubluetooth   usocket   ussl   ujson   ure   ntptime
webrepl   upip   neopixel   framebuf   dht   ds18x20   onewire   btree
_gc / math / uctypes / uzlib / uhashlib / ucryptolib / uasyncio ...
```

- **WiFi 实测可用**：`network.WLAN().active(True)` 成功，`scan()` 扫到 **16 个热点**
- **BLE 可用**（`ubluetooth`）、**TLS 可用**（`ussl`）、**WebSocket 可用**（`uwebsocket`）
- ⚠️ **没有 `urequests`**（可用 `upip` 安装，或直接用 `usocket` 手写 HTTP）
- ⚠️ 官方手册提示：**WiFi DNS 失败（-202）**时需手动
  `wlan.ifconfig((ip, mask, gw, '114.114.114.114'))`

---

## 7. 与第 2 代（COM10 / COM11）的差异总览

| 维度 | **COM13（第 1 代）** | COM10 / COM11（第 2 代） |
|---|---|---|
| 芯片 | ESP32-C3，单核 160 MHz | ESP32-S3，双核 240 MHz |
| 显示 | **5×5 红点阵**（N32 驱动） | ST7735 TFT 160×128（SPI） |
| 主控模块 | `control_board_v1` | `controlBoardAlphaPiOne` |
| N32 UART | `tx=8 rx=9 @460800` | `tx=3 rx=0 @460929` |
| 传感器 I2C | `scl=7 sda=6 @400k`，**0x18** | `scl=9 sda=8 @100k`，扩展板 0x20/0x21 |
| 灯光 | WS2812 **14 颗**（GPIO5） | WS2812 / LED 模块 |
| 按键 | **3 个**（GPIO 10/20/21） | 3 个 + 摇杆 + 4 键（仅 COM11） |
| 输入丰富度 | 加速度计 + 人体红外 + 麦克风 | 摇杆/电位器/超声波/温湿度/心率… |
| 音频 | N32 `0x10/0x11/0x12/0x14/0x15` | 同协议（第 2 代也复用 N32） |
| 中文字库 | **无**（只有 94 项 ASCII 5×5 字模） | HZK16 + gb2312 + `sysfont` |
| 网络 | `network` / `ubluetooth` / `ussl`（**原版 MicroPython 全功能**） | 热点 + UDP 广播封装在 `controlBoardAlphaPiOne` 里 |
| 连接要求 | **DTR 无关** | COM11 必须 DTR=1/RTS=0 |
| 文件数 | 21 | 62 / 74 |

---

## 8. 作品方向（可落地）

| # | 作品 | 用到的资源 | 难度 |
|---|---|---|---|
| 1 | **联网滚动时钟 / 信息屏** | WiFi + `ntptime` + `led_show_string_async` + 3 按键 | ★（已实现：见 §9） |
| 2 | **体感游戏机** | 加速度计 `IsForward` + 3 按键 + 点阵 + 音频 | ★★ |
| 3 | **给 AlphaPiCar 当体感遥控端** | WiFi/UDP + 加速度计（复用车项目的协议） | ★★ |
| 4 | **语音留言盒 / 智能门铃** | 麦克风录音 ≤20 s + 人体红外 + 喇叭 | ★★ |
| 5 | **联网语音播报** | 绕过固件，直接往 N32 `0x15` 灌自定义 16k PCM + `usocket` 取 TTS | ★★★ |
| 6 | **氛围灯 / 音乐律动灯** | 14 颗 WS2812 + `pixelShowU` / `ShowRainbow` | ★ |

> 最推荐 #1 起步：#3 要两块板、#5 要自己实现 N32 流式写，而 #1 只依赖单板 + WiFi，
> 且能立刻跑通"固件完全跑不动它"的完整闭环（配置 → 联网 → 取时 → 显示 → 按键交互）。

---

## 9. 实战：联网滚动时钟

工程位置：[`../projects/AlphaPiClock/`](../projects/AlphaPiClock/README.md)。

要点（细节与部署命令见该工程 README）：

| 设计点 | 做法 | 原因 |
|---|---|---|
| 滚动显示 | `control_board_v1.led_show_string_async()` | **N32 自己会滚动**，同步版 `led_show_string` 会 `sleep_ms(len*128)` 阻塞 3–4 秒 |
| 主循环 | 每帧 `next(soundLoop)` + `UpdateButtonStatus()` | 固件要求；否则音频与按键全停 |
| 取时 | `ntptime.settime()` → `time.localtime(time.time() + 8*3600)` | `ntptime` 给的是 UTC，需手动加时区 |
| DNS | 连上后 `wlan.ifconfig((ip, mask, gw, '114.114.114.114'))` | 规避手册记录的 DNS `-202` |
| 秒指示 | 灯带 14 颗按秒递增点亮 | 顺手用掉板载灯带，且不干扰主显示 |
| 按键 | A 切模式 / B 强制对时 / C 报时开关，**边沿检测** | 长按不能连触发 |

---

## 10. 踩坑与注意

1. **不要执行 `control_board_v1.get_files_from_flash()`**（只存在于旧档那版 `main.py`）。
   它是从裸 Flash `0x160000` 恢复文件系统的逻辑，误调用有覆盖风险。
2. **打开串口会打断当前程序**，板子停在 REPL；调试完请
   `python tools/repl_probe.py COM13 reset` 让 `main.py` 重新跑起来。
3. **音频是半双工**：播放前必须先写 `0x10 = 0` 停录。
4. **`actuator_led.InitNP()` 的参数是 GPIO 号**（示例传 `5`），灯珠数固定 14，不是参数。
5. **`DataStruct` 必须包**：`actuator_led` / 底层 TFT 一类接口要求动态类型包装。
6. **N32 通信偶发卡死** → 失败重试 + 连续写两次。
7. **`WritePwm` 每次调用都 `deinit` 重建 PWM 对象**，高频调用要注意开销。
8. **没有中文点阵**：5×5 字模只有 94 项 ASCII。
9. **改完文件必须复位**，否则 `sys.modules` 缓存里跑的还是旧代码。
10. `mpremote fs cp -r` 的目标目录**必须先存在**。

---

## 11. 待确认 / 后续可做

1. `r1.dat`（364 KB）与旧档 `r1.dat`（53 KB）的具体内容（IMA ADPCM 解码后听一遍）。
2. 5×5 点阵的**亮度**是否可调（N32 寄存器表里没看到对应项）。
3. GPIO `3` 扩展口的实际丝印/外设（Demo 未使用）。
4. 尝试复用 N32 的 `0x15` 音频流接口播放**自定义 PCM**（16k/16bit/mono），
   为"联网 TTS 语音播报"打底。
5. 加速度计两种批次（`0x12` / `0x18`）的寄存器差异实测。

---

## 附录 A：启动与 REPL 日志（2026-09-26 实测）

```
$ python tools/serial_log.py COM13 115200 6
OPENED COM13 @ 115200, DTR=1, sending Ctrl-C ...

Traceback (most recent call last):
  File "main.py", line 45, in <module>
KeyboardInterrupt:
MicroPython v1.19.1-1-g71a8956f6-dirty on 2022-08-08; ESP32C3 module with ESP32C3
Type "help()" for more information.
>>>
--- 227 bytes received ---
```

`main.py:45` = 出厂 Demo 主循环里的 `loop1HasNext = next(loop1)`，
即当时正卡在"等 `r1.dat` 播完"。

## 附录 B：本次扫描的原始产物

| 位置 | 内容 |
|---|---|
| `firmware/com13_20220808/rootfs/` | 板载 21 个文件的**全量备份** |
| `firmware/com13_20220808/MANIFEST.md` | 逐文件 SHA256 校验清单 |
| `board_dump/com13/` | 探查阶段用 `repl_probe.py get` 导出的模块与 `main.py`（已校验与全量备份一致） |
| `../projects/AlphaPiClock/` | 基于本报告开发的第一件作品 |
