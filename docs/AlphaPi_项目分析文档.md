# AlphaPi One 项目分析文档

> **实机对应**：COM10 = **循迹小车**（厂商定制固件），COM11 = **游戏机**（自编译通用固件）。
> 实机取证结果见 `AlphaPi_循迹小车（COM10）分析报告.md` 与 `AlphaPi_游戏机（COM11）分析报告.md`；
> 本文分析的是仓库内的静态资料（`firmware/v2020_07_31/`、`firmware/v1.0.3/`），与实机版本存在代际差异。

> **文档地图**
>
> | 文档 | 主题 | 适用对象 |
> |---|---|---|
> | `AlphaPi_循迹小车（COM10）分析报告.md` | COM10 实机取证、固件分层、文件系统、N32 协议 | **循迹小车** |
> | `AlphaPi_游戏机（COM11）分析报告.md` | COM11 实机取证、控制链路、打砖块游戏实战 | **游戏机** |
> | `AlphaPi_实机调试指南.md` | REPL 使用、shell 命令对照、上传与调试流程 | **两块板通用** |
> | 本文 | 仓库历史固件（`firmware/v2020_07_31/` 2020 版、`v1.0.3`）与手册要点 | 背景资料 |

> 本文基于对仓库内源码、`.mpy` 反汇编产物、示例工程、Flash 备份以及《AlphaPi One 技术参考手册 v4》的完整通读整理。
> 文中所有 API 参数、寄存器地址、常量值均来自反汇编实际字节码或手册原文；无法确定之处已标注「推断」。

---

## 1. 项目概述

AlphaPi（灵犀 / 核桃编程生态）是一块面向青少年编程教育的 **ESP32-S3 开发板**，出厂预装一套 **MicroPython 定制固件**，内置图形化编程（类似 Scratch）的运行时系统。

本仓库（`lingxi/AlphaPi`）**不是**厂商的固件源码工程，而是一份**逆向研究与二次开发资料库**，内容包括：

- 从电路板提取的 4MB Flash 全量备份与 rootfs 文件系统；
- 关键 `.mpy` 模块的反汇编文本（用于还原封装 API）；
- 可运行的示例代码（LED / 加速度计 / 按键）；
- 官方技术参考手册 PDF；
- 一个较新版本的固件目录 `firmware/v1.0.3/`（厂商更新后的模块）。

README 原文特别强调：

> 注意！！AlphaPi 电路板的硬件版本和固件随时都在更新，这个项目的固件是比较老的版本，请一定要先提取自己板子上的固件版本，先做好备份！

因此本项目的定位是：**固件取证 + API 还原 + 玩法探索**。

---

## 2. 仓库结构

```
AlphaPi/
├── README.md                              # 项目说明 + 已还原的 API 摘要 + GPIO 对应表
├── LICENSE
├── AlphaPi_One_技术参考手册_v4.pdf         # 官方技术参考手册（v3 正文 + v4 新增章节）
├── firmware/v2020_07_31/examples/                               # 可运行的示例代码
│   ├── 01_LED(OFFICAL METHODS)/main.py    # 官方 5x5 LED API 用法
│   ├── 02_ACCEL/main.py                   # SC7A20 三轴加速度计直读
│   ├── 03_BUTTON/main.py                  # 按键封装类
│   └── 04_LED(WITH SOURCE CODE)/main.py   # 手写 UART 协议驱动 5x5 LED
├── test/
│   ├── test.py                            # 单行内容：../..//pycdc/test.py（反编译调试残留）
│   └── test.mpy
├── firmware/v2020_07_31/                                   # 旧固件（提取现场）
│   ├── AlphaPi_flash_4MB.bin              # 4MB Flash 全量 dump
│   ├── rootfs/                            # 从 Flash 恢复的文件系统
│   │   ├── boot.py / main.py / main2.py / variable.py
│   │   ├── control_board_v1.mpy / basic.mpy / actuator_led.mpy / sensor_infrared.mpy
│   │   └── *.dat                          # 13 个音频资源文件
│   └── mpy_disassemble/                   # 反汇编产物
│       ├── control_board_v1.mpy.txt       # 131KB 反汇编（核心）
│       ├── basic.mpy.txt                  # 52KB
│       ├── actuator_led.mpy.txt           # 41KB
│       ├── sensor_infrared.mpy.txt        # 2.2KB
│       ├── *.mpy.freeze                   # 冻结字节码
│       └── control_board_v1.mpy.decompiled
└── firmware/v1.0.3/                                # 较新版本固件
    ├── main.py
    └── rootfs/
        ├── boot.py / main.py
        ├── basic.mpy / controlBoard.mpy   # 模块已更名
        └── *.dat（13 个音频资源）
```

---

## 3. 硬件平台

### 3.1 核心规格

| 项目 | 规格 |
|---|---|
| 主控 | ESP32-S3，240MHz 双核，40MHz 晶振 |
| 屏幕 | ST7789（兼容 ST7735 命令集），128×160，SPI |
| 音频协处理器 | **N32** 芯片，通过 UART1 通信 |
| Flash | 8MB XMC（OPI 模式） |
| PSRAM | 有（SPIRAM） |
| 无线 | WiFi 2.4GHz + BLE（不支持 A2DP） |
| USB 桥接 | HETAO/N32 芯片，VID:PID `2F4E:0102` |

### 3.2 引脚映射（来自反汇编实测 + 手册）

**ESP32-S3 侧引脚（固件实际使用）**

| 功能 | GPIO | 说明 |
|---|---|---|
| 屏幕 MOSI | 35 | SPI |
| 屏幕 SCK | 37 | SPI |
| 屏幕 MISO | 38 | SPI |
| 屏幕 CS | 33 | SPI |
| 屏幕 DC | 36 | SPI |
| 屏幕 RST | 10 | 与按键 A 复用同一引脚号 |
| 屏幕背光 BL | 11 | PWM 可调 |
| 按键 A | 10 | `Pin.IN + PULL_DOWN` |
| 按键 B | 20 | `Pin.IN + PULL_DOWN` |
| 按键 C | 21 | `Pin.IN + PULL_DOWN` |
| I2C SCL / SDA | 7 / 6 | `SoftI2C`，400kHz |
| NeoPixel 灯带 | 5（示例） | 外部 RGB 灯带，14 颗 |
| UART1 TX / RX | 8 / 9（旧固件）/ 3 / 0（小智固件） | 与 N32 协处理器通信 |
| P1 / P2 | 5 / 4 | README 中标记为「未知」（后经手册确认为 I2C，见 §12） |

> 注意：README 中记录的 UART 为 `TX 8 / RX 9, baudrate=460800`；反汇编常量实际为 `460800`（手册写 `460929`，两者接近，应为手册笔误或自适应波特率）。
> 另有版本信息提示「N32 芯片可能支持自适应波特率」。

**I2C 从机地址（自动扫描判定）**

固件启动时执行 `i2c.scan()[0]` 作为 `addr`，并据此初始化加速度计：

| 扫描到的地址 | 芯片 | 初始化写操作 |
|---|---|---|
| `0x12` (18) | 国产三轴（如 SC7A20 兼容型号） | `writeto_mem(0x12, 0x11, b'\xc4')` |
| `0x18` (24) | 另一型号加速度计 | `writeto_mem(0x18, 0x20, b'\x27')` |

---

## 4. 固件分层架构

### 4.1 启动流程

```
上电
 ├─ boot.py                 空壳（仅注释掉的 webrepl 启动代码）
 ├─ main.py
 │   ├─ 检查文件系统：若 os.listdir() 文件数 < 阈值
 │   │     → get_files_from_flash()  从 Flash 0x160000 处的文件表恢复文件
 │   └─ import protocal as p; p.check_hardware()
 └─ 进入应用 / 图形化运行时
```

`main.py` 的核心是**从裸 Flash 中恢复文件系统**，这解释了为什么这个仓库能拿到完整 rootfs。其文件表格式（推断）：

```
[4 字节 大端长度][28 字节 文件名（0xFF 填充）][文件内容...]
重复直至长度 > 1000000 视为结束
```

`firmware/v2020_07_31/rootfs/main.py` 每 64KB 分块写盘，`firmware/v1.0.3/rootfs/main.py` 改为一次性写入（更简洁）：

```1:39:firmware/v1.0.3/rootfs/main.py
addr = 0x160000
def readFile(length:numbers):
    global addr
    temp_buf = bytearray(length)
    esp.flash_read(addr, temp_buf)
    addr+=length
    return temp_buf
```

### 4.2 运行时分层

```
┌──────────────────────────────────────────────┐
│ 应用/图形化积木程序 (main.py 生成的 Loop 循环)  │
├──────────────────────────────────────────────┤
│ control_board_v1.mpy  主控板抽象层             │
│   LED / 音量 / 按键 / 录音播放 / 加速度 / GPIO  │
├──────────────┬───────────────┬───────────────┤
│ basic.mpy    │ actuator_led  │ sensor_infrared│
│ DataStruct   │ NeoPixel 灯带 │ 红外传感器     │
├──────────────┴───────────────┴───────────────┤
│ machine / esp / time / math / os             │
├──────────────────────────────────────────────┤
│ UART1 ──► N32 协处理器（音频/5x5 LED/按键）    │
│ I2C   ──► 加速度传感器                        │
└──────────────────────────────────────────────┘
```

**关键设计特征**：

1. **两级 MCU 架构**：教育板的复杂外设（音频编解码、5×5 点阵 LED、按键扫描）由国产 **N32** MCU 承担，ESP32-S3 只通过 UART 发送命令帧。
2. **弱类型动态变量系统**：`basic.DataStruct` 把所有变量包装成可动态转型的容器，以支撑图形化编程中「变量没有固定类型」的语义。
3. **生成器驱动的协作式多任务**：`Loop1()`、`play_record_loop()`、`wait_time()` 全是 `yield` 生成器，主循环每帧 `next(...)` 一次，实现非阻塞并发（见示例 01）。

---

## 5. 核心模块 `control_board_v1.mpy` API 全解

- 源文件：`control_board_v1.py`，编译产物 8.07KB
- 版本字符串：**`v_2020_7_31`**
- 模块级依赖：`machine(ADC, PWM, Pin, SoftI2C)`、`gc`、`time`、`math`、`os`

### 5.1 模块级全局对象

| 名称 | 初始化值 | 作用 |
|---|---|---|
| `i2c` | `SoftI2C(scl=Pin(7), sda=Pin(6), freq=400000)` | 传感器总线 |
| `addr` | `i2c.scan()[0]` | 加速度计从机地址 |
| `pin_map` | `{3: Pin(3, OUT, value=1), 10: Pin(10,IN,PULL_DOWN), 20: ..., 21: ...}` | GPIO 惰性缓存表 |
| `uart` | `UART(1, 460800, tx=8, rx=9, timeout=100)` | N32 协处理器通道 |
| `pa/pb/pc_last_status` | `0` | 三个按键的上次电平 |
| `nextMission` / `currentMission` | `None` | 录音/播放任务队列 |
| `charPointMap` | 94 项字典 | 字符 → 5 字节列点阵 |
| `defaultCharPointMap` | `bytearray([0,0,0,0,0])` | 缺字兜底（空白） |
| `showIndex` | `0` | LED 显示帧序号（用于同步等待） |

### 5.2 UART 协处理器协议层

固件实现了三种帧：

**写帧**
```
[0x90][addr][len][data...][checksum]
响应：[0x91][addr][checksum]  → 函数返回 resp[2]
```

**读帧**
```
[0x80][addr][count]
响应：[0x81][addr][len][data...][checksum]  → 长度 = count + 4
```

**校验和**
```python
checksum = (0x90 + addr + len + data...) & 0xFF   # 除末字节外全部累加
```

| 函数 | 签名 | 行为 |
|---|---|---|
| `calc_checksum(data)` | `(data) -> int` | 累加 `data[0..len-2]`，返回 `& 0xFF` |
| `uart_write(addr, data)` | `(addr, data) -> int \| False` | 组写帧并发送，回读 3 字节；成功返回 `resp[2]`，否则打印 `write error:` 并返回 `False`；`len(data)==0` 直接 `False` |
| `uart_write_buf(addr, data)` | `(addr, data) -> None` | 大数据分块发送，每块之间 `sleep_ms(10)`，直到写完 |
| `uart_read(addr, count)` | `(addr, count) -> bytearray` | 单次读；校验失败打印 `checksum error` 并返回 `b'\x00'` |
| `uart_read_buf(addr, count)` | `(addr, count) -> bytearray` | 分批读，每批最多 **200 字节**；先 `gc.collect()`；拼接所有数据返回 |

`uart_read_buf` 分批实现（读头部 3 字节，第 3 字节是本批长度，再读「长度+1」字节）：

```1491:1510:firmware/v2020_07_31/mpy_disassemble/control_board_v1.mpy.txt
  raw bytecode: 137 5a:2e:7a:81:46:81:37:80:23:...
  prelude: n_state=12, n_exc_stack=0, scope_flags=0, n_pos_args=2, ...
  args: ['addr', 'count']
```

报错标识：`'checksum error'`、`'write error: '`、`err1`（录音读头长度 ≠ 3）、`err2`（实际读长 ≠ 声明长度）。

### 5.3 加速度传感器（SC7A20 系列）

| 函数 | 签名 | 行为 |
|---|---|---|
| `GetAccelerationRaw()` | `() -> [x, y, z]` | 读原始三轴数据 |
| `GetAcceleration(axial)` | `(axial) -> int` | `axial < 3` 返回对应轴；`>= 3` 返回 `round(sqrt(x²+y²+z²))` 合加速度 |

原始数据读取逻辑（两种芯片分支）：

- `addr == 0x12`：`readfrom_mem(0x12, 0x01, 6)`
- `addr == 0x18`：`readfrom_mem(0x18, 0xA8, 6)`

随后按高位/低位合成 16-bit，`> 32767` 时 `-65536` 转有符号，最后全部 `>> 4` 得到 **12 位带符号数**。

示例代码 `firmware/v2020_07_31/examples/02_ACCEL/main.py` 中的 `transdata()` 与该算法完全一致：

```10:22:firmware/v2020_07_31/examples/02_ACCEL/main.py
def transdata(l,m):
    a=int.from_bytes(m,'big')
    b=int.from_bytes(l,'big')
    temp=a<<8|b
    temp=temp>>4
    temp=temp&0x0fff
    ...
```

> 示例直接把加速度计挂在 `I2C(scl=Pin(7), sda=Pin(6), freq=500000)`，并读寄存器 `0x0f` 校验 ChipID（期望 `0x11`）、写 `0x20` 设置 100Hz 输出率——这与固件内的 `addr==0x18` 分支寄存器不同，说明板子存在**至少两种加速度计批次**。

**姿态判定**

| 函数 | 签名 | 逻辑 |
|---|---|---|
| `CheckForward(acc, x_mid, y_mid, z_mid, margin)` | 5 参数 | 三轴偏差均 `< margin` 时返回 `True`（即“处于中位”） |
| `IsForward(forward)` | `(forward) -> bool` | 基于原始加速度判断 6 个方向（1~6），阈值 `±700`，且横轴 `abs < 300` |

`IsForward` 方向定义（推断）：

| forward | 条件 |
|---|---|
| 1 | `y < -700` |
| 2 | `y > 700` |
| 3 | `z < -700 且 |x| < 300 且 |y| < 300` |
| 4 | `z > 700 且 |x| < 300 且 |y| < 300` |
| 5 | `x > 700` |
| 6 | `x < -700` |

### 5.4 GPIO / ADC / PWM

| 函数 | 签名 | 行为 |
|---|---|---|
| `ReadPin(pin_port)` | `(pin_port) -> int` | 惰性创建 `Pin(pin_port, IN)` 存入 `pin_map`，返回电平 |
| `WritePin(pin_port, value)` | `(pin_port, value) -> None` | 惰性创建 `Pin(pin_port, OUT)`，写电平 |
| `ReadAdc(pin_port)` | `(pin_port) -> int` | `ADC(Pin)` + `atten(ATTN_11DB)` + `read_u16() >> 6` → 返回 **10 位**值 |
| `WritePwm(pin_port, value)` | `(pin_port, value) -> None` | 销毁重建 `PWM`，`freq(1000)`，`Clamp(value, 0, 1023)` 后 `duty()` |

> `WritePwm` 每次调用都 `deinit()` 再重建 PWM 对象，属于「简单粗暴但可控」的实现，代价是频繁重建。

### 5.5 按键系统

| 函数 | 签名 | 行为 |
|---|---|---|
| `UpdateButtonStatus()` | `() -> str` | 读取 A/B/C 三键电平存入 `pa/pb/pc_last_status`，返回 `"a_b_c"` 拼接字符串 |
| `GetLastPinStatus(pin_port)` | `(pin_port) -> int` | 按 10/20/21 返回缓存状态，其他返回 `0` |

示例 `firmware/v2020_07_31/examples/03_BUTTON/main.py` 在用户态重新实现了更完整的 `Button` 类（`is_pressed` / `was_pressed` / `get_presses` / `irq`），直连 GPIO 10 / 20 / 21，可作为固件 `UpdateButtonStatus` 的高层替代。

### 5.6 5×5 点阵 LED 与字符串显示

固件通过写寄存器 `0x08` 驱动 N32 上的 5×5 红光点阵。

| 函数 | 签名 | 行为 |
|---|---|---|
| `led_show_bytes_async(show_bytes)` | `(bytearray) -> None` | `uart_write(0x08, bytes)`，`showIndex += 1` |
| `led_show_bytes(show_bytes)` | `(bytearray) -> None` | 调 async 后阻塞等待：长度 >5 时 `sleep_ms((len-5)*100 + 400)`，否则 `sleep_ms(400)` |
| `led_show_string_async(s)` | `(str) -> int` | 取前 10 个字符，逐字符查 `charPointMap` 拼接点阵（每字 5 字节），缺字用 `defaultCharPointMap`，补 `0x00` 间隔，写 `0x08`，返回总字节长度 |
| `led_show_string(s)` | `(str) -> None` | 调 async，按返回长度 `sleep_ms(len*128)` 或 `sleep_ms(256)` |

点阵编码规则（README 原文）：
- `bytearray([8,0,0,0,0])` → 第 5 行第 1 列
- `bytearray([16,0,0,0,0])` → 第 4 行第 1 列
- `bytearray([128,0,0,0,0])` → 第 1 行第 1 列
- `bytearray([255,255,255,255,255])` → 全亮

每个字节对应一列（5 位有效位掩码 `0x08|0x10|0x20|0x40|0x80`）。

**字符集**：`charPointMap` 含 94 项，覆盖 `0-9`、`a-z`、`A-Z` 及常见符号（`` ` ~ ! @ # $ % ^ & ( ) _ = [ ] { } \ | ; : ' " , . < > ? + - * / ``），另有「空格」等——即一套 **5×5 ASCII 字模表**。

### 5.7 录音 / 播放（PlayRecordMission）

这是固件中最复杂的部分：一个基于 **步进状态机** 的半双工音频任务系统。

**`PlayRecordMission` 类**

| 方法 | 说明 |
|---|---|
| `__init__(is_recording, file_name, sec=…)` | 初始化；`sec` 默认 20 且被限制为不超过 20；`step=0`；`count=200`；`read_len=0`；`playing_buf=bytearray(200)`；录音模式额外分配 `uart_buf=bytearray(202)`、`byte_to_write=bytearray(b'\x80\x11\x08')`、`rec_buf=bytearray(4096)`、`recordingBufCnt=sec*6` |
| `isFinish()` | `step == 4` |
| `interrupt()` | 中断当前任务：`__stop()` 后按状态置 `step=4` 或 `step=3`（并切到 `record_end.dat`） |
| `__tickRecord()` | 录音推进：开文件、发 `uart_write(0x10, [1])` 开录、分块读 `0x11` 麦克风 PCM 存盘 |
| `__tickPlay()` | 播放推进：开文件、发 `uart_write(0x10, [0])` 停录（半双工）、循环 `uart_write(0x15, block)` 写 200 字节音频流 |
| `__stop()` | 若正在录音且 `step==2`，发 `uart_write(0x10, [0])` 停止并关文件 |
| `tickStep()` | 状态机主推进（录音/播放两条路径） |

**状态机 `step` 流转（录音）**

```
0  →  1  (切换 currentFileName = record_start.dat，先播提示音)
1  →  2  (__tickPlay 播完提示音 → 切回目标 fileName，开始录音)
2  →  3  (__tickRecord 收满 → currentFileName = record_end.dat)
3  →  4  (播完结束音 → isFinish)
```

**对外任务接口**

| 函数 | 签名 | 说明 |
|---|---|---|
| `PushPlayRecordMission(is_record, file_name, sec=…)` | 3 参数 | 创建任务并压入 `nextMission`，同时 `interrupt()` 掉旧的 `nextMission` / `currentMission` |
| `play_record_loop()` | 生成器 | 主循环泵：切换 current/next、驱动 `tickStep()`、`yield True` |
| `playAsync(path)` | `(path)` | 若文件存在，压入播放任务（异步） |
| `playUntilDone(path)` | 生成器 | 压入播放任务并 `yield` 到 `isFinish()` |
| `play(path)` | `(path)` | 阻塞式播放：直接开文件循环 `uart_write_buf(0x15, block)` 直到文件结束 |
| `recAsync(path, sec=…)` | 2 参数 | 压入录音任务（异步） |
| `recUntilDone(path, sec=…)` | 生成器 | 压入录音任务并 `yield` 到 `isFinish()` |
| `stopRecord()` | `()` | 若 currentMission 正在录音，调用 `interrupt()` |
| `rec(path, sec=…)` | 2 参数 | 阻塞式录音完整实现（见下） |

**`rec()` 阻塞实现要点**

1. `sec` 超过 20 时钳制为 20；
2. 先 `play('record_start.dat')` 播提示音；
3. `uart_write(0x10, bytearray([1]))` 开启录音（寄存器 `0x10 = AUDIO_CTRL`）；
4. 外层循环 `sec * 6` 轮，每轮分配 `bytearray(4096)` 缓冲；
5. 内层循环：发 `b'\x80\x11\x08'` 读麦克风（寄存器 `0x11`），`readinto` 读头 3 字节 → 再读数据，按 `err1` / `err2` 校验，写入 `rec_buf`；
6. 缓冲写满后 `file.write(rec_buf)`；
7. 结束：`uart_write(0x10, [0])` 关闭录音，`play('record_end.dat')`。

半双工约束（手册第 21 页）：**播放时必须先关闭录音**（写 `0x10 = 0`），播放结束后可恢复。

### 5.8 音量 / 工具函数

| 函数 | 签名 | 行为 |
|---|---|---|
| `read_volume()` | `() -> int` | `uart_read(0x12, 1)[3]`，返回寄存器 `0x12` 的第一个数据字节 |
| `Clamp(value, min_value, max_value)` | `(v, min, max) -> 数值` | 上下限截断 |
| `average(nums)` | `(list) -> float` | 求和 / 长度 |
| `GetSysTime()` | `() -> int` | `time.ticks_ms()` |
| `voidCommand()` | `() -> 0` | 空操作占位（图形化积木中的「空语句」） |
| `version()` | `() -> 'v_2020_7_31'` | 模块版本 |

---

## 6. `basic.mpy` —— DataStruct 动态类型运行时

- 版本字符串：**`v_2020_7_31`**
- 依赖：`time`、`random`、`math`
- 常量池：`[180.0, 'v_2020_7_31', 0.0, 0.5, 1.401298e-07]`

### 6.1 设计思想

`DataStruct` 是**图形化编程的运行期动态变量容器**：内部只保存一个 `value`，对外提供一整套**类型自适应**的取值与运算接口。所有算术 / 比较运算符都返回**新的 `DataStruct` 实例**，从而模拟脚本语言中「变量无固定类型、表达式结果仍是变量」的语义。原板 TFT 驱动也要求参数必须用 `DataStruct` 包装后传入底层 C 函数（见手册第 6 页 Q3）。

### 6.2 类方法（30 项）

| 类别 | 方法 |
|---|---|
| 构造 / 赋值 | `__init__(self, v)`、`SetValue(self, v)` |
| 取原始值 | `StringValue`、`IntValue`、`FloatValue`、`NumberValue`、`BoolValue` |
| 类型判定 | `IsInt`、`IsNumber` |
| 长度 / 查找 | `length`（定义两次，后者生效）、`find(self, other)`、`contains` |
| 算术 | `__add__`、`__radd__`、`__iadd__`、`__sub__`、`__mul__`、`__truediv__`、`__mod__` |
| 比较 | `__lt__`、`__gt__`、`__le__`、`__ge__`、`__eq__`、`__ne__` |
| 数学 | `__round__(n=…)`（带默认参数）、`__abs__`、`__ceil__`、`__floor__` |

> 反汇编显示 `length` 在类体内被 `STORE_NAME` 两次（一次在 `find` 附近，一次在 `contains` 之后），即**后定义覆盖前定义**。

### 6.3 模块顶层函数

| 函数 | 签名 | 功能 |
|---|---|---|
| `wait_time(time_ms)` | 生成器 | 非阻塞延时：`ticks_ms` 差值 `< time_ms` 时 `yield True`，超时 `yield False` |
| `data_struct_random(v1, v2)` | 2 参数 | 自适应随机：全整型走 `randrange`，否则走浮点线性插值 |
| `data_struct_and(v1, v2)` | 2 参数 | 逻辑与（短路） |
| `data_struct_or(v1, v2)` | 2 参数 | 逻辑或（短路） |
| `data_struct_substring(v1, f, start, end)` | 4 参数 | 子串截取，`f==2` 时倒序；先交换保证 `start <= end` |
| `data_struct_normalization(v, min1, max1, min2, max2)` | 5 参数 | 区间归一化 / 线性映射 `(v-min1)/(max1-min1)*(max2-min2)+min2`，带截断 |
| `DegreeToRadian(v)` | 1 参数 | `v * π / 180` |
| `RadianToDegree(v)` | 1 参数 | `v * 180 / π` |
| `ClampD(value, min_value, max_value)` | 3 参数 | 数值截断 |
| `FindDataInList(list_variable, data)` | 2 参数 | 按字符串比较查找，返回索引，未找到返回 `-1` |
| `GetItemFromList(list_variable, index_data)` | 2 参数 | 越界返回 `DataStruct('')`，否则返回元素 |
| `version()` | 0 参数 | 返回 `'v_2020_7_31'` |

---

## 7. `actuator_led.mpy` —— NeoPixel RGB 灯带

- 版本字符串：**`v_2020_7_30`**
- 依赖：`neopixel`、`machine`、`basic.DataStruct`
- 全局：`brightness = 10`（0–100）、`np = None`、`rawRGB = []`

### 7.1 初始化

```python
# InitNP(pin_port) 反汇编还原
np = neopixel.NeoPixel(machine.Pin(pin_port), 14)   # 14 颗灯珠
rawRGB = [(0, 0, 0)] * 14
np.write()
```

> 示例代码调用 `actuator_led.InitNP(5)`，因此灯带接 **GPIO5**，共 **14 颗** WS2812。

### 7.2 函数清单

| 函数 | 签名 | 说明 |
|---|---|---|
| `InitNP(pin_port)` | 1 参数 | 创建 NeoPixel(14)，清空 |
| `BrightnessUp(br_d)` | 1 参数 | `brightness += br_d.IntValue()`，Clamp 到 0–100 |
| `SetBrightness(br_d)` | 1 参数 | 直接设置亮度（Clamp 0–100） |
| `UpdateBrightness()` | 0 参数 | 按 `brightness*255//100` 比例刷新所有灯珠 |
| `GetBrightness()` | 0 参数 | 返回当前亮度 |
| `ShowRainbow()` | 0 参数 | HSV 彩虹循环（`np.n <= 0` 时直接返回） |
| `setPixelColor(index, rgb)` | 2 参数 | 打包 RGB 后写点并 `np.write()` |
| `setPixelColorWithoutWright(index, r, g, b)` | 4 参数 | 写入但不刷屏；`index >= n` 时按环绕处理 |
| `setPixelColorWithoutWrightRGBOne(index, rgb)` | 2 参数 | 解包 RGB 后调用上一函数 |
| `pixelMove(...)` | — | 像素移动 / 流水效果 |
| `pixelShowU(value_d, max_value_d)` | 2 参数 | **音量条效果**：清空 0–13，按 `value > k*(max/6)` 依次点亮，颜色 绿→黄→橙→红 |
| `clamp(minValue, maxValue, value)` | 3 参数 | 注意参数顺序为 (min, max, value) |
| `hsl(h, s, l)` | 3 参数 | HSL → RGB 打包 |
| `packRGB` / `packRGBd` / `unpackR` / `unpackG` / `unpackB` | — | RGB 值打包 / 解包 |
| `version()` | 0 参数 | 返回 `'v_2020_7_30'` |

`pixelShowU` 的分段阈值与颜色（反汇编常量）：

| 段 | 阈值条件 | 颜色 (R,G,B) |
|---|---|---|
| 1–2 | `value > max/6` | (255, 255, 0) 黄 |
| 3–4 | `value > 2*max/6` | (255, 204, 0) |
| 5–6 | `value > 3*max/6` | (255, 153, 0) |
| 7–8 | `value > 4*max/6` | (255, 102, 0) |
| 9–10 | `value > 5*max/6` | (255, 51, 0) |

这说明官方「音量显示」积木就是靠 `actuator_led.pixelShowU(DataStruct(read_volume()), DataStruct(255))` 实现的（见 `firmware/v2020_07_31/rootfs/main.py` 的 `proc_1`）。

---

## 8. `sensor_infrared.mpy` —— 红外传感器

- 版本字符串：**`v_2020_7_30`**
- 依赖：`machine.Pin`、`control_board_v1.pin_map`

```python
def read_infrared_sensor(pin_port):
    pin_map[pin_port] = Pin(pin_port, Pin.IN)   # 复用主控板的 pin_map 缓存
    return pin_map[pin_port].value()

def version():
    return 'v_2020_7_30'
```

设计要点：**跨模块复用 `control_board_v1.pin_map`**，避免重复创建 Pin 对象。

---

## 9. 示例代码分析

### 9.1 `01_LED(OFFICAL METHODS)/main.py` —— 官方 API + 生成器并发

```16:34:firmware/v2020_07_31/examples/01_LED(OFFICAL METHODS)/main.py
def Loop1():
    control_board_v1.led_show_bytes_async(bytearray([128, 0, 0, 0, 0]))
    my_show_index = control_board_v1.showIndex
    time_waiting = wait_time(256)
    while next(time_waiting) and my_show_index == control_board_v1.showIndex:
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

- **亮点**：用 `showIndex` 快照 + `wait_time` 生成器实现非阻塞点灯动画，代码可直接映射为图形化积木（`Loop1` ≈ 一个「重复执行」积木）。
- `soundLoop = control_board_v1.play_record_loop()` 是音频主循环泵，必须每帧 `next()`。
- 顶层 `while True` 即图形化运行时的 scheduler。

### 9.2 `02_ACCEL/main.py` —— 绕过固件直读传感器

直接 `I2C(scl=Pin(7), sda=Pin(6), freq=500000)`，读 ChipID（`0x0f`）、写 `0x20=0x57`（100Hz）、按 `0x28~0x2d` 读六字节并做 12 位补码转换。**是理解固件 `GetAccelerationRaw` 的最佳参考实现。**

### 9.3 `03_BUTTON/main.py` —— 用户态按键类

提供 `is_pressed` / `was_pressed` / `get_presses`（软件去抖计数）/ `irq`（硬件中断）四种方式，直连 GPIO 10 / 20 / 21。

### 9.4 `04_LED(WITH SOURCE CODE)/main.py` —— 手写 UART 协议

不依赖任何 `.mpy`，用纯 MicroPython 复刻 N32 通信层：

```22:49:firmware/v2020_07_31/examples/04_LED(WITH SOURCE CODE)/main.py
def calc_checksum(data : bytearray):
    sum = 0
    for i in range(0,len(data)-1):
        sum+=data[i]
    return sum&0xff

def uart_write(addr, data:bytearray) -> num:
    #与国产MCU通信，格式为头帧0x90+地址+数据长度+数据+累加和校验值
    #如通信成功会返回3bytes数据b'\x91\x08\x05',有时通信会卡死，原因未知，连续写两次则必定成功，奇怪？？？
    ...
    for i in range(0,2):   # 连续写两次规避卡死
        uart.write(byteToWrite)
        ansbytes = uart.read(3)
        ...
```

**重要发现**：作者在注释中记录了 N32 通信会偶发卡死，**连写两次必定成功**。固件原版 `uart_write` 没有这个重试，是示例作者总结的工程 trick。

示例还内置了数字 `0-9` 的 5×5 字模 `number_map`，与固件 `charPointMap` 的编码方式完全一致。

---

## 10. 文件系统与 Flash 布局

| 项目 | 值 |
|---|---|
| 文件表起始地址 | `0x160000`（old 与 v1.0.3 均为该值） |
| 表项格式 | `[4B 大端长度][28B 文件名, 0xFF 填充][内容]` |
| 结束条件 | 长度字段 `> 1000000` |
| 恢复触发条件 | `len(os.listdir()) < 10`（old）/ `< 15`（v1.0.3） |
| 分块大小 | old: 64KB 分块写；v1.0.3: 一次性写 |

音频资源文件（13 个 `.dat`）：`alert`、`broken`、`drop`、`du`、`electric`、`funny`、`msg`、`pass`、`record_start`、`record_end`、`right`、`tech`、`wrong`。
格式为自定义音频（手册第 6 页称为 **IMA ADPCM**），通过 `0x15` 寄存器流式播放。

提取与反编译命令（README）：

```shell
# 提取 4M flash
esptool -p /dev/cu.usbmodem101 read_flash 0 0x400000 flash_contents.bin
# 反汇编 mpy
micropython/tools/mpy-tool.py -d ./rootfs/control_board_v1.mpy > ./rootfs/control_board_v1.mpy.txt
```

---

## 11. 版本演进（`firmware/v2020_07_31/` → `firmware/v1.0.3/`）

| 项目 | old | v1.0.3 |
|---|---|---|
| 主控板模块名 | `control_board_v1.mpy` (8.07KB) | `controlBoard.mpy` (9.58KB) |
| 灯带模块 | `actuator_led.mpy` | 已合入 / 未单独提供 |
| 红外模块 | `sensor_infrared.mpy` | 已合入 / 未单独提供 |
| `basic.mpy` | 3.08KB | 3.06KB |
| `main.py` 恢复阈值 | 文件数 < 10 | 文件数 < 15 |
| 分块写盘 | 64KB 分块 | 一次性写 |
| 音频 `.dat` | 13 个 | 13 个（同名同大小） |

**结论**：`v1.0.3` 是厂商迭代版，主控模块改名为 `controlBoard` 并增大约 1.5KB（功能有扩充），音频资源保持不变。由于 v1.0.3 未提供反汇编，其新增 API 仍需自行用 `tools/mpy-tool.py` 反编译确认。

---

## 12. 技术参考手册 v4 要点

手册正文标题为 v3（2026-08-28），文末追加 v4 新章节，覆盖**三种固件状态**：

| 特性 | 原板（定制固件） | 通用版（MicroPython） | 小智固件（AI 助手） |
|---|---|---|---|
| 开发语言 | MicroPython | MicroPython | C++ / ESP-IDF |
| 屏幕 | ST7735.mpy | 需自行实现 | ST7789 + LVGL9 |
| 中文显示 | HZK16 + `textzh` | 需自行实现 | Noto Sans |
| 音频 | .dat/.wav/.ima | 仅 16kHz PCM | Opus + N32 |
| 语音识别 | ✗ | ✗ | WakeNet9 + MultiNet5 |
| AI 对话 | ✗ | ✗ | ✓ |
| HTTPS | ✗ | `ssl` + `urequests` | mbedTLS |
| OTA | ✗ | ✗ | 双分区 OTA |
| DataStruct | 必需 | 不需要 | N/A |
| 音频波特率 | 460929 | 460929 | 1 Mbps |

### 12.1 N32 协处理器寄存器表（手册 §6.4）

| 地址 | 名称 | 读写 | 说明 |
|---|---|---|---|
| `0x00` | KEY | 读 | 按键状态，A 键 = bit2 (`0x04`) |
| `0x10` | AUDIO_CTRL | 写 | 录音控制：1 = 开，0 = 关 |
| `0x11` | AUDIO_READ | 读 | 读取麦克风 PCM |
| `0x12` | — | 读 | 固件 `read_volume()` 实际读的地址 |
| `0x14` | VOLUME | 写 | 音量 0–100 |
| `0x15` | AUDIO_STREAM | 写 | 音频流写入（播放），每块 200 字节 |

### 12.2 音频参数

- 16kHz / 16-bit signed little-endian / mono PCM
- 每块 200 字节 = 100 样本 = 6.25ms
- 播放前必须停录（半双工）

### 12.3 原板 TFT 的 DataStruct 约定

原板底层 TFT API **必须**用 `DataStruct` 包装参数，否则报 `function takes N positional arguments`：

| API | 正确用法 |
|---|---|
| text | `tft.text(DataStruct(...))` |
| fill | `tft.fill(DataStruct(color))` |
| rect | `tft.rect(DataStruct(...))` |

这印证了 §6 中「DataStruct 是运行时类型桥梁」的判断。

### 12.4 v4 新增：另一款 12864 LCD 子板（文中标注为「新板」）

手册附录（中文部分因 PDF 字体编码问题部分乱码，以下为可辨认内容）：

| 项目 | 参数 |
|---|---|
| LCD | LX-12864L，ST7565 兼容，SPI |
| 分辨率 | 128 × 64，2.0 寸 |
| 显示结构 | 16 字符 × 4 行（8×16 点阵） |
| MCU | **N32G031F8S7**，I2C 从机 + SPI 主控 |
| I2C 从机地址 | `0x09` |
| I2C 引脚 | SCL = **GPIO5**，SDA = **GPIO4** |
| I2C 速率 | 50kHz |

这正好解答了 README 中「P1 — GPIO5、P2 — GPIO4 未知」的疑问：**这两脚是 I2C 总线，用于驱动 12864 LCD 子板**。

手册提供了完整的 MicroPython 驱动 `walnut_lcd.py`（`WalnutLCD` 类）：

```python
class WalnutLCD:
    def __init__(self, scl=5, sda=4, addr=0x09):
        self.i2c = machine.SoftI2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=50000)
        ...
    def show(self, lines):   # 4 行文本
    def icon(self, icon_id): # 图标
    def flip(self, invert):  # 翻转显示
```

驱动注意事项（手册原文）：I2C 速率需 ≤50kHz；每次发送后延时 0.03s；N32G031 接收缓冲有限（需分 4 次发 64 字节）。

### 12.5 常见问题速查

- **WiFi DNS 失败（-202）**：需手动 `wlan.ifconfig((ip, mask, gw, '114.114.114.114'))`。
- **通用版无 MP3 解码器**：网络收音机需换 Arduino + ESP32-audioI2S。
- **小智固件白屏**：其帧缓冲为 320×240，需调 offset 适配 128×160 屏幕。
- **原板 TFT 报参数错误**：用 `DataStruct` 包装参数。

---

## 13. 关键发现与遗留问题

### 13.1 值得关注的设计

1. **N32 双芯架构**：ESP32-S3 只做「大脑」，音频 / 点阵 / 按键扫描全部下放给 N32，通过 UART 的 `0x90/0x80` 帧协议交互。这是理解整块板的关键。
2. **`DataStruct` 是图形化运行时的类型基石**：不仅用于变量运算，连底层 TFT 参数也要求它，属于「运行时到处都要用它」的强耦合设计。
3. **生成器协作式调度**：`wait_time`、`play_record_loop`、`recUntilDone`、示例 `Loop1` 统一用 `yield` 表达「等待/并发」，与 Scratch 的「等待 N 秒」「重复执行」一一对应。
4. **`pin_map` 惰性缓存 + 跨模块共享**：`sensor_infrared` 直接复用 `control_board_v1.pin_map`，属于为省内存做的优化。
5. **Flash 内嵌文件系统**：固件从 `0x160000` 的裸文件表恢复文件，说明出厂时文件系统是「烧进 Flash 的镜像」。

### 13.2 已知缺陷 / 风险点

| 问题 | 位置 | 说明 |
|---|---|---|
| N32 通信偶发卡死 | 示例 04 注释 | 需连写两次；固件原版无重试 |
| `uart_read` 无重试 | `control_board_v1` | 校验失败直接返回 `b'\x00'` |
| `WritePwm` 反复重建 PWM 对象 | `control_board_v1` | 效率与副作用需注意 |
| `length` 方法被重复定义 | `basic.DataStruct` | 前一个定义失效 |
| `rec` 内 `sec` 硬上限 20 | `control_board_v1` | 单次录音最长约 20 秒 |
| UART 参数不一致 | README(460800) / 手册(460929) | 建议实测确认 |
| v1.0.3 无反汇编 | `firmware/v1.0.3/` | 新版 API 未知 |
| 模块名错拼 `protocal` | 原板 `main.py` | 实际导入名就是 `protocal`，勿改成 `protocol` |

### 13.3 后续可做的工作

1. 用 `tools/mpy-tool.py` 反汇编 `firmware/v1.0.3/rootfs/controlBoard.mpy`，与 `control_board_v1` 做 diff。
2. 补齐 `charPointMap` 全部 94 个字模（可从反汇编常量池提取，用于自制字符）。
3. 尝试复用 N32 的 `0x15` 音频流接口播放自定义 PCM（16k/16bit/mono）。
4. 验证 `0x12`（读音量）与 `0x14`（写音量）的配合关系。
5. 为 N32 通信层补上「失败重试」以规避示例中记录的卡死问题。

---

## 14. 快速上手速查表

```python
import control_board_v1

# 5x5 点阵
control_board_v1.led_show_bytes(bytearray([255,255,255,255,255]))   # 全亮
control_board_v1.led_show_string("HI")
control_board_v1.led_show_string_async("OK")

# 加速度
x, y, z = control_board_v1.GetAccelerationRaw()
g = control_board_v1.GetAcceleration(3)      # 合加速度
if control_board_v1.IsForward(5): ...        # 倾斜判定
control_board_v1.CheckForward((x,y,z), 0, 0, 900, 300)

# 按键
control_board_v1.UpdateButtonStatus()
control_board_v1.GetLastPinStatus(10)        # A 键

# GPIO
control_board_v1.WritePin(3, 1)
control_board_v1.WritePwm(3, 512)
v = control_board_v1.ReadAdc(3)              # 10 位

# 音频（需每帧泵 play_record_loop）
loop = control_board_v1.play_record_loop()
control_board_v1.play('alert.dat')
control_board_v1.playAsync('msg.dat')
control_board_v1.rec('my.dat', 5)
control_board_v1.PushPlayRecordMission(False, 'alert.dat', 0)

# 音量
vol = control_board_v1.read_volume()
```

```python
# 灯带（NeoPixel，14 颗，默认接 GPIO5）
import actuator_led
from basic import DataStruct
actuator_led.InitNP(5)
actuator_led.SetBrightness(DataStruct(50))
actuator_led.ShowRainbow()
actuator_led.pixelShowU(DataStruct(control_board_v1.read_volume()), DataStruct(255))
```

```python
# 动态变量（图形化运行时核心）
from basic import DataStruct, wait_time, data_struct_normalization
a = DataStruct("12")
n = a.IntValue()                 # 12
r = data_struct_normalization(DataStruct(50), DataStruct(0), DataStruct(100),
                              DataStruct(0), DataStruct(255))   # 线性映射
```

---

*文档基于仓库当前内容整理，硬件/固件版本差异较大时请以实机为准。*
