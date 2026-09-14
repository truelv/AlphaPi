# AlphaPi 循迹小车（COM10）分析报告

> **设备归属（用户确认）**
>
> | 串口 | 角色 | 枚举信息 |
> |---|---|---|
> | **COM10** | **循迹小车** | `VID_2F4E:PID_0102`（HETAO/N32 USB 桥接） |
> | **COM11** | **游戏机** | `VID_303A:PID_4001`（ESP32-S3 原生 USB-Serial/JTAG） |
> | COM7 | 无关设备 | `VID_2BDF:PID_028A`，君正（Ingenic）Linux 设备 |
>
> 本报告分析的是 **COM10 循迹小车**；游戏机（COM11）的分析见 `AlphaPi_游戏机（COM11）分析报告.md`。

> 本报告基于**串口实机取证**（COM10，MicroPython REPL + raw REPL 内省 + `.mpy` 反汇编），
> 描述用户手上这块 AlphaPi One 的真实固件状态。
> 采集日期：2026-09-13。产物保存在 `firmware/com10_20221028/rootfs/`，工具为 `tools/serial_log.py`、`tools/repl_probe.py`。

---

## 当前固件与运行状态

> 板上的固件和程序都可能被替换，**引用本文数据前请先核对这里**。
> 下表状态实测于 2026-09-13（此后该板已离线，现状未复核）。

| 项目 | 值 | 来源 |
|---|---|---|
| MicroPython 版本 | `3.4.0; MicroPython 25d2a8a04 on 2022-09-30` | `sys.version` |
| platform | `esp32` | REPL |
| Board 标识 | **`AlphaPi One with ESP32S3`**（**厂商定制**固件） | 启动横幅 |
| **开机自启程序** | `main.py` → **`ht_main.py`（683B）** ＝ *只开 Wi-Fi 热点* | 文件系统 |
| 板上文件总数 | 60 | `os.listdir()` |
| 出厂标识 | `SW_VER: 2022102803` / `HW_NAME: ONE \| Oct 28` | `board_info()` |
| 主控模块 | `controlBoardAlphaPiOne.mpy` → `v_2023_03_28` | `version()` |
| Flash | 8388608（8MB），factory 分区 `0x10000` / 1376256 | `esp` / `esp32.Partition` |

**两个易混点**：

1. `sys.version` 开头的 `3.4.0` 是 **Python 语言版本**，不是 MicroPython 内核版本。
2. 本机是 **2022-10-28 批次**（`SW_VER: 2022102803`），比手册记录的新板
   （`SW_VER: 23111501 / Nov 15`）更早，与仓库 `firmware/v2020_07_31/`（2020 版）更不是同一代。

> **这块板的出厂程序只做一件事**：开机 1 秒后**开启 Wi-Fi 热点 `aiphapione` / `12345678`**，
> 然后进入主循环什么都不做。所以被动监听串口收到 0 字节属于正常现象，
> 必须发 `Ctrl-C` 才能进入 REPL。

---

## 0. 一句话摘要

这块板子运行的是 **2022-10 硬件 + 2023-03 固件**，与仓库 `firmware/v2020_07_31/` 目录里那份 2020 年固件
**不是同一代产品**：屏幕从 5×5 LED 点阵升级为 **ST7735 TFT（160×128）**，新增了
**图形化图层（Label/图表）、WiFi/热点/UDP 广播、蜂鸣器节拍音乐、中文字库**等能力，
且 UART/SPI 引脚全部变更。

---

## 1. 实机识别

| 项目 | 值 | 来源 |
|---|---|---|
| 串口 | COM10（`VID_2F4E:PID_0102`，HETAO/N32 桥接） | 设备枚举 |
| MicroPython | `3.4.0; MicroPython 25d2a8a04 on 2022-09-30` | REPL |
| platform | `esp32` | REPL |
| Flash | 8388608 (8MB) | `esp.flash_size()` |
| factory 分区 | addr `0x10000`, size 1376256 | `esp32.Partition.find()` |
| 出厂版本 | `SW_VER: 2022102803` / `HW_NAME: ONE \| Oct 28` | `board_info()` |
| 主控模块版本 | `controlBoardAlphaPiOne` → **`v_2023_03_28`** | `version()` |
| basic 模块版本 | **`v_2022_11_30`** | `version()` |
| 内存 | free 48528 / alloc 120432 | `gc` |
| 文件数 | 60 | `os.listdir()` |

> 对比：手册记录新板出厂标识为 `SW_VER: 23111501 / HW_NAME: ONE | Nov 15`，
> 本机是 **2022-10-28 批次**，属于更早的一批。

---

## 2. 与仓库现有资料的关系（重要）

| 维度 | 仓库 `firmware/v2020_07_31/`（2020 版） | 仓库 `firmware/v1.0.3/` | **本机（2023-03 版）** |
|---|---|---|---|
| 主控模块 | `control_board_v1.mpy` | `controlBoard.mpy` | `controlBoardAlphaPiOne.mpy` |
| 模块版本 | `v_2020_7_31` | — | **`v_2023_03_28`** |
| basic 版本 | `v_2020_7_31` | — | **`v_2022_11_30`** |
| 显示 | 5×5 点阵 LED | — | **ST7735 TFT 160×128** |
| UART(TX/RX) | 8 / 9 @460800 | — | **3 / 0 @460929** |
| SPI | 无 | — | **2 @20MHz, sck41/mosi42/miso45** |
| I2C | scl7/sda6 @400k（姿态传感器） | — | **car: scl9/sda8 @100k** |
| 中文字库 | 无 | — | **HZK16 + gb2312 + sysfont.mpy** |
| 网络 | 无 | — | **WiFi/热点/UDP 广播** |

**结论**：`firmware/v2020_07_31/` 的反汇编分析（5×5 LED、UART 8/9）对本机**基本不适用**，
必须以北报告 + `firmware/com10_20221028/rootfs/` 为准。

---

## 3. 硬件配置（实机实测，权威）

```
UART(1, baudrate=460929, bits=8, parity=None, stop=1,
     tx=3, rx=0, txbuf=256, rxbuf=256, timeout=100)
     ↑ N32 音频协处理器（与手册第 3 页一致）

SPI(id=2, baudrate=20000000, polarity=0, phase=0, bits=8,
    sck=41, mosi=42, miso=45)
     ↑ 屏幕总线（与手册第 2 页的 35/37/38 不同，是另一版硬件）

TFT(spi, dc=39, reset=38, cs=40) → initr() → rgb(True) → fill(BLACK) → rotation(1)
```

**I2C 扩展口**（新发现）：

```python
i2c_info_map = {'car': {'freq': 100000, 'sda': 8, 'scl': 9}}
```

即 **GPIO8=SDA / GPIO9=SCL**，用于外接「小车」类扩展模块。
（注意：这正是 `firmware/v2020_07_31/` 版里 N32 通信占用的两个脚，说明硬件改版后它们被释放给了 I2C。）

**按键位掩码**：`keyP = [128, 64, 32, 16, 8, 4, 2, 1]`

**引脚对**：

```python
PinPair = {1:{'t':10,'r':11}, 2:{'t':12,'r':13}, 3:{'t':14,'r':17}, 4:{'t':18,'r':48}}
```

---

## 4. 启动链与源码（明文，已导出）

### 4.1 `boot.py`（120B）

```python
import protocal as p

b = p.uart_read(0,1)[3]
if b&0x0C == 0x0C:
    import factory_reset

static_buf=bytearray(40960)
```

- 启动时读 N32 寄存器 `0x00`（按键状态）第 1 字节；
- 若 bit2/bit3（`0x0C`）**同时**置位（按键组合）→ 导入 `factory_reset` 触发恢复出厂；
- 分配 **40KB** `static_buf`，供屏幕背景缓冲使用。

> 关键点：`protocal` 是**真实模块名**（拼写错误但被固化），不是 `protocol`。
> 且它**不在文件系统中**——是编译进固件的 **frozen 模块**。

### 4.2 `main.py`（43B）

```python
import ht_main


ht_main.Start(static_buf)
```

`static_buf` 来自 `boot.py`——MicroPython 把 `boot.py` 与 `main.py` 先后执行在同一个
`__main__` 命名空间，因此 boot 里的全局变量能被 main 直接引用。

### 4.3 `ht_main.py`（683B，出厂示例程序）

```python
import variable
import time
time.sleep_ms(1000)
import math
import basic
from basic import DataStruct
from basic import wait_time
import controlBoardAlphaPiOne


def Loop1():
    controlBoardAlphaPiOne.openHotspot(DataStruct("aiphapione"), DataStruct("12345678"))
    yield False


loop1 = Loop1()
loop1HasNext = True


def Start(static_buf):
    controlBoardAlphaPiOne.init()
    controlBoardAlphaPiOne.InitBackground_buf(static_buf)
    soundLoop = controlBoardAlphaPiOne.play_record_loop()
    loop1 = Loop1()
    loop1HasNext = True
    while True:
        controlBoardAlphaPiOne.Update()
        next(soundLoop)
        if loop1HasNext:
            loop1HasNext = next(loop1)
```

**出厂示例行为**：开机 1 秒后初始化，然后**自动开启 Wi-Fi 热点**
`aiphapione` / `12345678`。若你搜到这个热点，就是这块板发的。

主循环仍是**生成器协作式调度**：`Update()` + 音频泵 `soundLoop` + 用户 `loop1`，
每帧各 `next()` 一次——与 2020 版架构一脉相承。

### 4.4 其他明文文件

| 文件 | 大小 | 内容 |
|---|---|---|
| `variable.py` | 63B | `defaultVariable = DataStruct(0)` |
| `music.py` | 25B | `def Update(): return` |
| `pen.py` | 25B | `def Update(): return` |
| `testok` | 2B | `ok`（出厂测试标记，**存在**） |

> 主控模块在导入时会**自动重写** `music.py` 与 `pen.py` 为上述占位函数（反汇编中可见
> `open('music.py','w')` 写入 `def Update():\n    return\n`）。

---

## 5. 文件系统清单（60 项）

```
HZK16|267616              ST7735.mpy|8182           alert.dat|20782
autoMotionOne.mpy|4274    basic.mpy|3393            boot.py|120
controlBoardAlphaPiOne.mpy|22339                   drop.dat|27694
du.dat|16322              electric.dat|37486        funny.dat|26542
gb2312|83607              ht_main.py|683           logo2.bmp|8694
main.py|43                max30102.mpy|8333         msg.dat|17686
music.py|25               pass.dat|18478           pen.py|25
record_end.dat|17686      record_start.dat|21428    remoteControlActuatorOne.mpy|1769
remoteControlSensorOne.mpy|915                     right.dat|20782
steeringEngineActuatorAlphaPiOne.mpy|597           sysfont.mpy|2519
tech.dat|29422            testok|2                 variable.py|63
wrong.dat|24812
+ 约 30 个 *.htbmp 图片（2568B / 1448B）
```

**新增的积木驱动模块**（2020 版没有）：

| 模块 | 大小 | 推测功能 |
|---|---|---|
| `autoMotionOne.mpy` | 4274 | 自动运动（预设动作） |
| `remoteControlActuatorOne.mpy` | 1769 | 遥控执行器 |
| `remoteControlSensorOne.mpy` | 915 | 遥控传感器 |
| `steeringEngineActuatorAlphaPiOne.mpy` | 597 | 舵机执行器 |
| `max30102.mpy` | 8333 | 心率血氧传感器 |

**音频资源**（13 个 `.dat`）：alert / broken / drop / du / electric / funny / msg /
pass / record_start / record_end / right / tech / wrong。

**图片资源**（`.htbmp`）：方向箭头（forward / left_front / left_rear / right_front /
right_rear / back / clockwise / anti_clockwise）、车灯（high_beam / dipped_beam）、
表情（happy / sad / angry? / likes）、传感器图标（temperature / humidity / sensor /
sound / time / heart / data / record）、实物（car / boy / girl / stone / gold）等。

---

## 6. 模块 API 全集

### 6.1 `controlBoardAlphaPiOne`（`v_2023_03_28`）

**基础设施**：`init`、`version`、`Update`、`board_info`、`InitBackground_buf`

**底层协议**：`calc_checksum`、`uart_read`、`uart_read_buf`、`uart_write`、`uart_write_buf`、`play`、`rec`

**屏幕绘制**：`TFT`、`TFTColor`、`showString`、`showStringBase64`、`showStringWithPos`、
`showStringBase46WithPos`、`showStringWithXY`、`showStringBase46WithXY`、`showPointWithXY`、
`showLine`、`showLineBase64`、`clearScreen`、`Color16`、`Color32To16`

**中文显示**：`textzh`、`charzh`、`getGB2312`、`q2b`

**图层 / Label**：`Label`、`LabelType`、`LabelValue`、`LabelTextValue`、`LabelIconValue`、
`get_label_index`、`update_label_layer`、`SetLabelLayer`、`SetLabelColor`、
`ShowLabelTextAtPosWithSize`、`ShowLabelTextBase64AtPosWithSize`、
`ShowLabelTextAtXYWithSize`、`ShowLabelTextBase64AtXYWithSize`、
`ShowLabelIconAtPosWithSize`、`ShowLabelIconAtXYWithSize`、`HideLabel`、
`build_background`、`update_foreground`

**图表**：`LineChart`、`BarChart`

**音频**：`play_record_loop`、`PlayRecordMission`、`PushPlayRecordMission`、`playAsync`、
`playUntilDone`、`recAsync`、`recUntilDone`、`stopRecord`、`stopPlay`、
`read_volume`、`checkVolume`、`set_volume`

**蜂鸣器 / 节拍音乐**：`BuzzerMission`、`buzzerMission`、`beatTimeMs`、`playBeat`、
`playBeatAsync`、`playBeatList`、`playBeatListAsync`、`playBeatRealTime`、
`playBeatListRealTime`、`beatMusicMap`、`beatBpm`

**网络**：`network`、`socket`、`ujson`、`ubinascii`、`openHotspot`、`connectWifi`、
`setToken`、`broadcast`、`broadcastWithValue`、`hasBroadcast`、`getBroadcastValue`、
`recv_udp`、`send_udp`、`ReceiveOnce`、`IsWifiConnect`、`IsHotspotOpened`

**GPIO / 工具**：`Clamp`、`average`、`GetSysTime`、`ReadPin`、`WritePin`、`ReadAdc`、
`WritePwm`、`SetPwm`、`Init_I2c`、`getStatus`、`voidCommand`、`PinPair`

**关键全局量**：

| 名称 | 值（实测） | 含义 |
|---|---|---|
| `screen_width` / `screen_height` | `160` / `128` | 横屏尺寸 |
| `status_list` | `[0]*22` | 22 项状态缓存 |
| `attitude_map` | `[(64,6),(4,7),(8,8),(16,9),(32,10),(1,11),(2,12),(128,13),(256,14)]` | 姿态位掩码 → status 索引 |
| `beatBpm` | `120` | 默认节拍速度 |
| `sysfont_zh16` | `{'Width':16,'Height':16}` | 16×16 中文字库描述 |
| `temp_buf` | `memoryview(bytearray(4608))` | 字模临时缓冲 |
| `char_a` | `bytearray(32)` | 单汉字 32 字节点阵缓存 |
| `ASCII_TABLE` | 列表（约 1520 项） | 8×16 ASCII 点阵字库 |
| `gb2312_1` | 94 项 dict | 符号区码表 |
| `label_list` | 12 个 `Label` 对象 | 图层标签池 |
| `background_list` / `foreground_list` | `[]` / `[0..11]` | 背景/前景层索引 |
| `PinPair` | 4 组 `{t,r}` | 定时/量程引脚对 |
| `pwm_freq` | `{}` | 端口→PWM 频率 |
| `i2c_info_map` | `{'car': {'freq':100000,'sda':8,'scl':9}}` | 扩展 I2C |
| `wifi_token` | `''` | 广播令牌 |
| `sta_if` / `ap_if` | `WLAN(STA_IF)` / `WLAN(AP_IF)` | 网络接口 |
| `udp_r` / `udp_s` | `None` | UDP 收发套接字 |
| `receive_map` / `receive_message` | `{}` / `[]` | 广播接收缓存 |

### 6.2 `protocal`（frozen 模块，无源码文件）

公开 API：
`hal`、`zlib`、`esp`、`machine`、`time`、`os`、`uart`、`tft`、`TFT`、`TFTColor`、
`keyP`、`addr`、`calc_checksum`、`uart_read`、`uart_read_buf`、`uart_write`、
`uart_write_buf`、`play`、`rec`、`update_mcu`、`board_info`、`screen_init`、
`showBmp`、`check_hardware`、`showString`、`progress`、`readFile`、
`get_files_from_flash`、`init_files`、`lastProgress`、`t1`、`t_reset`、`t2`、`t3`

- `addr` = **1441792** = `0x160000` → **文件表起始地址**（与 2020 版一致）
- `hal` → 硬件抽象层（手册提到可用 `hal.gpio_map` 取引脚名）
- `init_files` / `get_files_from_flash` / `readFile` → 从裸 Flash 恢复文件系统
- `progress` / `t1..t3` / `lastProgress` → 进度与超时管理

### 6.3 `basic`（`v_2022_11_30`）

与 2020 版基本一致：`DataStruct`（30 个方法）、`wait_time`、`data_struct_random`、
`data_struct_and`、`data_struct_or`、`data_struct_substring`、`data_struct_normalization`、
`DegreeToRadian`、`RadianToDegree`、`ClampD`、`FindDataInList`、`GetItemFromList`、`version`

**新增**：`ClampBlock`（图形化「限制范围」积木）。

### 6.4 `ST7735`（屏幕驱动）

- 无独立版本字符串；`ScreenSize = (128, 160)`（竖屏基准，rotation 后互换）
- 颜色为 **RGB565**：`((R&0xF8)<<8) | ((G&0xFC)<<3) | (B>>3)`
- `TFT` 类方法：`size`、`on`、`invertcolor`、`rgb`、`rotation`、`pixel`、`line`、
  `vline`、`hline`、`rect`、`fillrect`、`circle`、`fillcircle`、`fill`、`image`、
  `text`、`char`、`setvscroll`、`vscroll`、`initr`、`initb`、`initb2`、`initg`
- 字体通过参数 `aFont` 传入（字典含 `Start`/`End`/`Width`/`Height`/`Data`），
  **不依赖 sysfont 模块**
- 初始化序列 `COLMOD=0x05`（16bit/RGB565）；`rotation` 通过 MADCTL 与
  `TFTRotations=[0,96,192,160]` 实现
- `offset` 机制补偿物理面板偏移（`initb2` 用 `[2,1]`）

---

## 7. 关键子系统

### 7.1 显示与图层系统

- `init()` 建立 SPI→TFT（21 号构造函数路径），`rotation(1)` 得到 160×128 横屏
- `InitBackground_buf(static_buf)` 把 boot.py 的 40KB 缓冲变成 `memoryview` 背景层
- 12 个 `Label` 对象构成图层池；`background_list`（后层）与 `foreground_list`（前层）
  用索引列表排序，`update_label_layer` / `SetLabelLayer` 调整层级
- `LineChart` / `BarChart` 提供图形化数据可视化积木
- `showString*` 系列有「自动换行光标」`screen_next_x/y`
- `Base46` 是源码里的拼写错误（应为 Base64），API 名沿用至今

### 7.2 音频与蜂鸣器

- **音频**：沿用 N32 协议（`play`/`rec`/`PlayRecordMission`），
  `read_volume` / `checkVolume` / `set_volume` 管理音量，`stopPlay` 新增
- **蜂鸣器节拍音乐**：
  - `beatBpm = 120`，`beatMusicMap` 内置 6 首曲子的音符序列
  - `beatTimeMs` 按 BPM 换算单拍时长
  - `playBeat` / `playBeatAsync`（单音）、`playBeatList` / `playBeatListAsync`（序列）、
    `playBeatRealTime` / `playBeatListRealTime`（实时）

### 7.3 网络与多机通信

- `openHotspot(ssid, pwd)` / `connectWifi(ssid, pwd)` / `IsWifiConnect` / `IsHotspotOpened`
- **UDP 广播**：`broadcast` / `broadcastWithValue` / `hasBroadcast` / `getBroadcastValue`
  配合 `receive_map`（`message → value`）与 `receive_message`（消息名列表），
  用于多块板子之间的「广播/接收」积木
- `setToken` / `wifi_token` 做身份标识
- `recv_udp` / `send_udp` / `ReceiveOnce` 为底层收发

### 7.4 按键与姿态

- `getStatus(DataStruct('0'))` 取按键（沿用手册 §2.6 用法）
- `attitude_map` 把 9 种方向位掩码映射到 `status_list[6..14]`
- `status_list` 22 项，末两位 `-150 / 150` 疑为加速度阈值（姿态判定用）

### 7.5 文件恢复机制

`protocal` 负责：`addr=0x160000` 处的文件表 → `readFile` / `get_files_from_flash` /
`init_files` 恢复到文件系统，并有 `progress` / `t1..t3` 做进度与超时保护。
本机文件系统已完整（60 个文件），说明恢复流程早已执行完成。

---

## 8. 三代固件对比

| 特性 | `firmware/v2020_07_31/`（2020） | `firmware/v1.0.3/` | **本机（2022-10 硬件 / 2023-03 固件）** |
|---|---|---|---|
| MicroPython | 2023-07-14 | — | **2022-09-30** |
| 主控模块 | control_board_v1 | controlBoard | controlBoardAlphaPiOne |
| 显示 | 5×5 LED 点阵 | — | **ST7735 TFT 160×128** |
| 中文显示 | ✗ | — | **HZK16 + gb2312 + sysfont** |
| 图层/图表 | ✗ | — | **12 Label + LineChart + BarChart** |
| UART | 8/9 @460800 | — | **3/0 @460929** |
| SPI | ✗ | — | **2 @20MHz (41/42/45)** |
| I2C | 7/6 @400k | — | **car: 9/8 @100k** |
| WiFi/广播 | ✗ | — | **✓** |
| 蜂鸣器音乐 | ✗ | — | **✓** |
| 积木驱动 | actuator_led 等 | — | autoMotion / remoteControl / steeringEngine |

---

## 9. 工具与产物

| 文件 | 说明 |
|---|---|
| `tools/serial_log.py` | 串口日志查看（`--follow` / `--no-ctrl-c` / `--hex` / `--no-dtr`，默认置 DTR） |
| `tools/repl_probe.py` | 通过 raw REPL 读写板子（`info` / `cat` / `get` / `put` / `rm` / `ls` / `run` / `reset`，DTR 自动处理） |
| `tools/mpy-tool.py` + `tools/makeqstrdata.py` | MicroPython 官方反汇编工具（v1.19.1） |
| `firmware/com10_20221028/rootfs/*.py` | 板载明文源码（main / ht_main / boot / variable / music / pen / testok） |
| `firmware/com10_20221028/rootfs/*.mpy` | 板载编译模块（controlBoardAlphaPiOne / basic / ST7735） |
| `firmware/com10_20221028/rootfs/*.mpy.txt` | 反汇编结果（391KB / 55KB / 157KB） |

**常用命令**：

```powershell
# 看启动日志
python tools/serial_log.py COM10 115200 8 --no-ctrl-c

# 进 REPL 采集信息
python tools/repl_probe.py COM10 info

# 执行任意代码
python tools/repl_probe.py COM10 run "import os; print(os.listdir())"

# 导出文件
python tools/repl_probe.py COM10 get sysfont.mpy ./firmware/com10_20221028/rootfs/

# 反汇编
python tools/mpy-tool.py -d firmware/com10_20221028/rootfs/xxx.mpy > firmware/com10_20221028/disasm/xxx.mpy.txt
```

> 连上终端之后怎么用（终端按键、shell 命令对照、`Ctrl-E` 粘贴模式、取"运行日志"、
> 三种开发方式），见 `AlphaPi_实机调试指南.md`——该文对 COM10 / COM11 两块板通用。

---

## 10. 待办与风险

### 待办
1. 反汇编 `sysfont.mpy`、`max30102.mpy`、`autoMotionOne.mpy`、`remoteControl*.mpy`、
   `steeringEngineActuatorAlphaPiOne.mpy`，补全积木生态。
2. 导出并备份 40 余个 `.htbmp` 图片与 `HZK16` / `gb2312` 字库（体积较大，分块导出较慢）。
3. 探测 `protocal` frozen 模块的行为（`check_hardware` / `board_info` / `screen_init` 输出）。
4. 弄清 `status_list` 22 项与 `attitude_map` 的完整对应关系。
5. ~~确认第二块板（疑似 COM11，`VID_303A:PID_4001` ESP32-S3 原生 USB）为何无输出。~~
   **已解决**：COM11 是游戏机（摇杆手柄硬件），"无输出"来自「必须 DTR=1 且 RTS=0」
   的 CDC 电平要求 + `ht_main.py` 主循环本身静默，详见
   `AlphaPi_游戏机（COM11）分析报告.md` §2.1（含 MobaXterm 连接配置）。

### 风险
- **两块板子不要混用同一套假设**：本报告只适用于 COM10 这块（2022-10 硬件）。
- `tools/repl_probe.py` 的 `get` 会持续占用串口，导出大文件时请勿同时打开其它串口工具。
- 出厂示例程序会自动开热点 `aiphapione`，如需干净环境可在 REPL 中打断 `main.py`。
- 未经确认不要执行 `factory_reset` 相关操作（`boot.py` 按键组合会触发恢复出厂）。

---

## 附：COM10 启动日志解读

```
boot:0x28 (SPI_FAST_FLASH_BOOT)   ESP32-S3 ROM 从 flash 启动
SPIWP:0xee / mode:DIO, clock div:1  flash 写保护与总线模式
load:0x3fcd0108,len:0xf24           加载 .dram 段
load:0x403b6000,len:0xc2c          加载 .iram 段
load:0x403ba000,len:0x2d60
entry 0x403b61f4                    跳转固件入口
HT protocol 0930                    应用层打印（核桃协议版本）
```

`HT protocol 0930` 之后没有更多输出是**正常的**——`ht_main.Start()` 进入
`while True` 主循环，不再打印。要看 REPL 需发 `Ctrl-C` 打断，实测可得到：

```
File "main.py", line 4, in <module>
File "ht_main.py", line 27, in Start
File "controlBoardAlphaPiOne.py", line 604, in Update
KeyboardInterrupt:
MicroPython 25d2a8a04 on 2022-09-30; AlphaPi One with ESP32S3
>>>
```

即主循环的阻塞点在 `controlBoardAlphaPiOne.py:604` 的 `Update()` 里。
