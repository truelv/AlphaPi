# AlphaPi 游戏机（COM11）分析报告

> **设备归属**
> - **COM11 = 游戏机**（用户命名）｜`USB\VID_303A&PID_4001`｜Windows 显示「USB 串行设备」
> - COM10 = 循迹小车｜`VID_2F4E:PID_0102`（HETAO/N32 桥接）→ 见 `AlphaPi_循迹小车（COM10）分析报告.md`
>
> 采集日期：2026-09-13。产物保存在 `firmware/com11_20220912/rootfs/`。

---

## 当前固件与运行状态

> 板上的固件和程序都可能被替换，**引用本文数据前请先核对这里**。
> 下表状态实测于 2026-09-13。

| 项目 | 值 | 来源 |
|---|---|---|
| MicroPython 内核 | **1.19.1** | `os.uname().release` |
| 编译来源 | `8e2a5ed99-dirty on 2022-09-12` | `os.uname().version` |
| Board 标识 | **`ESP32S3 module with ESP32S3`**（通用板，**非**厂商定制） | `os.uname().machine` |
| **开机自启程序** | `main.py` → **`ht_main.py`（6312B）** ＝ *小车接收端* | 文件系统 |
| 板上文件总数 | 75 | `os.listdir()` |
| 额外程序 | `game.py`（6272B）＝ *打砖块游戏*，**需手动启动，不自启** | 见 §10 |

**两个易混点**：

1. `sys.version` 开头的 `3.4.0` 是 **Python 语言版本**，不是 MicroPython 内核版本；
   内核版本要看 `os.uname().release`，本机为 **1.19.1**。
2. `dirty` 表示这份固件是**自行编译**的，而 COM10 是厂商定制固件
   （Board 标识 `AlphaPi One with ESP32S3`）——两块板不能混用同一套假设。

> **这块板插上电跑的是"小车接收端"程序**（`ht_main.py`）：它只等 Wi-Fi 广播再驱动电机，
> 摇杆和按键根本没被读取，所以作为"游戏机"是没反应的。
> 想玩游戏需手动启动 `game.py`，启动方法见 §10.4。

---

## 1. 一句话结论

COM11 **硬件是「摇杆手柄」**（2 轴摇杆 + 电位器 + 4 个按键，`remoteControlSensorOne` 驱动），
但**当前烧录的程序是「小车接收端」**（`ht_main.py`：收到 Wi-Fi 广播 → 驱动电机）。

即：**硬件是手柄，程序是小车**——两者不匹配，所以你看不到它"作为游戏机"的任何反应。

> ⚠️ 若要当手柄用，需要替换为「手柄端程序」：读摇杆 → `broadcast("上"/"下"/"左"/"右")`。
> 详见 §9「硬件确认与控制链路」。

---

## 2. 设备识别

| 项目 | 值 | 对比：COM10（循迹小车） |
|---|---|---|
| 串口 | COM11 | COM10 |
| USB | `VID_303A:PID_4001`，Espressif Device，序列号 `123456` | `VID_2F4E:PID_0102`（HETAO/N32 桥接） |
| USB 类型 | **ESP32-S3 原生 USB（应用自定义 CDC）** | 桥接芯片 UART |
| **DTR 要求** | **必须 DTR=1 且 RTS=0，否则无任何输出**（见 §2.1） | DTR 无关 |
| MicroPython | `3.4.0; 8e2a5ed99-dirty on 2022-09-12` | `3.4.0; 25d2a8a04 on 2022-09-30` |
| build 标识 | **`ESP32S3 module with ESP32S3`**（通用） | **`AlphaPi One with ESP32S3`**（定制） |
| 文件数 | **74** | 60 |
| factory 分区大小 | **2031616**（1.94MB） | 1376256（1.31MB） |
| 内存 | free 57152 / alloc 112512 | free 48528 / alloc 120432 |
| protocal 版本打印 | **`HT protocal 0913`** | `HT protocol 0930` |
| `boot.py` | 168B（标准 boot + `static_buf`） | 120B（含按键检测 + `factory_reset`） |
| `ht_main.py` | **6312B** | 683B |

> `8e2a5ed99-dirty` 的 "dirty" 表示这是一份**自行编译过的通用 MicroPython**，
> 而 COM10 是厂商定制固件。

### 2.1 关于 DTR（重要经验）

```
[DTR=1 RTS=0] 325 bytes   ← 唯一有输出的组合
[DTR=0 RTS=1] 0 bytes
[DTR=1 RTS=1] 12 bytes
[DTR=0 RTS=0] 0 bytes
```

连接这类设备**必须把 DTR 置位、RTS 保持低**（Arduino / TinyUSB 风格 CDC 的常见行为：
只有 DTR 拉高时才把数据发给主机）。由此衍生出三个必须记住的坑：

- **坑 1：DTR 不能在同一个串口句柄里翻转。** 实测先把 DTR 拉低、再拉高，就永久收不到
  数据了，`close()` 后重开也不一定恢复。**唯一可靠的姿势是打开端口后别动它**——
  pyserial / 多数终端打开端口时 DTR 默认就是置位的。
- **坑 2：RTS 必须为低。** 若流控选成 RTS/CTS，RTS 被置位，设备只吐 12 字节就哑了。
- **坑 3：程序本身不打日志。** `ht_main.py` 进入 `while True` 后零输出，被动监听 5 秒
  收到 **0 字节属于正常现象**，并不是没连上；必须发 `Ctrl-C` 打断才会出现 `>>>`。

#### 2.1.1 串口终端连接配置（MobaXterm，实测可用）

MobaXterm 新建 **Serial 会话**，按下表配置即可正常进入交互式 REPL：

| 设置项 | 值 | 说明 |
|---|---|---|
| Serial port | `COM11` | 别选成 COM7（那是君正 Linux 设备，与本项目无关） |
| Speed (baud) | `115200` | 原生 USB CDC 实际忽略波特率，填标准值即可 |
| Data bits / Stop bits / Parity | `8` / `1` / `None` | 标准 8N1 |
| **Flow control** | **`None`** | ← 关键。选 RTS/CTS 会触发坑 2，只收 12 字节 |

连上后窗口是黑的，**要手动敲几次 `Ctrl-C`** 才会出现 `>>>`（原因见坑 3）。
MobaXterm 没有 DTR 开关，但它的 DTR 默认状态恰好是置位的，所以可以直接用；
反过来，**别在别的工具里把 DTR 拉低之后再回来连**，那样往往要重新插拔 USB 才能恢复。

> 若打开端口时报 `Access denied` / `Cannot open`：串口同一时刻只能被一个程序打开。
> 先确认上次的串口标签页/会话真的关掉了，以及 VS Code、PuTTY、Arduino IDE 等没在占口。

#### 2.1.2 命令行工具（本项目）

工具已把 DTR 处理自动化，**不再需要手动加 `--dtr`**：

```powershell
python tools/serial_log.py COM11 115200 5            # 看日志（默认置 DTR，自动发 Ctrl-C）
python tools/serial_log.py COM11 115200 --follow     # 持续监听，Ctrl-C 退出
python tools/serial_log.py COM10 115200 8 --no-dtr   # 少数需要 DTR=0 的设备
python tools/repl_probe.py COM11 info                # 系统信息（DTR 自动处理）
python tools/repl_probe.py COM11 ls                  # 列出板上 74 个文件
python tools/usb_probe.py COM11 4                    # 轮询四种 DTR/RTS 组合，验证电平假设
```

> **连上终端之后怎么用**（终端按键、shell 命令对照、`Ctrl-E` 粘贴模式、取"运行日志"、
> 三种开发方式），见 `AlphaPi_实机调试指南.md`——该文对 COM10 / COM11 两块板通用。

#### 2.1.3 修改板上代码

`tools/repl_probe.py` 支持读写双向，标准流程：

```powershell
# 1) 先把板上原文件导回本地做备份
python tools/repl_probe.py COM11 get ht_main.py ./firmware/com11_20220912/rootfs/

# 2) 本地改好 ht_main.py ...

# 3) 上传覆盖（分块写入 + 自动长度校验）
python tools/repl_probe.py COM11 put ht_main.py

# 4) 软复位，让新代码生效
python tools/repl_probe.py COM11 reset
```

实测输出：

```
upload firmware/com11_20220912/rootfs/main.py -> _probe_tmp.py (43 bytes)
  board_size = 43 -> VERIFY OK
```

其它动作：`put 本地名 板载名`（另存为别的名字）、`rm 文件名`（删除）、`cat 文件名`（打印内容）。
`reset` 等价于在终端里按 `Ctrl-D`，会重新执行 `boot.py` / `main.py`。

另外，**esptool 无法连接**该口（`Failed to connect: No serial data received`），
因为 `PID_4001` 是应用自定义的 CDC 接口，不是 ROM 内置的 USB-Serial/JTAG，
所以拿不到 ROM bootloader。

---

## 3. 启动链

### 3.1 `boot.py`（168B）

```python
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

static_buf=bytearray(40960)
```

= **通用 MicroPython 的默认 `boot.py`** 模板 + 一行 40KB 缓冲区分配。
（对比 COM10 的 `boot.py` 有 N32 按键检测和 `factory_reset` 逻辑。）

### 3.2 `main.py`（43B）

```python
import ht_main


ht_main.Start(static_buf)
```

与 COM10 完全一致。

### 3.3 `ht_main.py`（6312B，主程序）

完整源码已导出到 `firmware/com11_20220912/rootfs/ht_main.py`。结构如下。

**公共初始化**：

```python
def Loop1():
    controlBoardAlphaPiOne.openHotspot(DataStruct("01"), DataStruct("01"))
    yield False
```

开机即开启 Wi-Fi 热点 **SSID = `01`，密码 = `01`**（对比 COM10 是 `aiphapione`/`12345678`）。

**6 组「触发器 + 动作」**：每组由一个 `LoopNTrigger` 监听广播指令，收到后执行 `LoopN`。

| 组 | 广播关键字 | 动作 | 电机功率 |
|---|---|---|---|
| Loop2 | `上` | `autoMotionOne.set_all_power(50, 50)` | 前进 |
| Loop3 | `下` | `autoMotionOne.set_all_power(-50, -50)` | 后退 |
| Loop4 | `左` | `autoMotionOne.set_all_power(50, -50)` | 左转 |
| Loop5 | `右` | `autoMotionOne.set_all_power(-50, 50)` | 右转 |
| Loop6 | `停` | `autoMotionOne.stop_motor(DataStruct('2'))` | 停止 |

触发器模式（以 Loop2 为例）：

```python
def Loop2Trigger(first):
    while True:
        if first:
            while controlBoardAlphaPiOne.hasBroadcast(DataStruct("上")):
                yield True
        while not controlBoardAlphaPiOne.hasBroadcast(DataStruct("上")):
            yield True
        break
    yield False
```

即：**等待广播出现 → 执行动作 → 等待广播消失 → 重新武装**。这是典型的
「边沿触发 + 去抖」状态机，避免长按导致动作反复触发。

**主循环**（第 162-217 行）统一泵所有生成器：

```python
    while True:
        controlBoardAlphaPiOne.Update()
        next(soundLoop)
        autoMotionOne.Update()
        if loop1HasNext:
            loop1HasNext = next(loop1)
        if loop2TriggerHasNext:
            loop2TriggerHasNext = next(loop2Trigger)
            if loop2TriggerHasNext is False and loop2HasNext is False:
                loop2 = Loop2()
                loop2HasNext = True
        if loop2HasNext:
            loop2HasNext = next(loop2)
            ...
```

`Trigger → 动作 → 重新武装 Trigger` 的完整闭环，6 组并排展开，是图形化积木
「当收到消息…」「重复执行」编译后的产物。

---

## 4. `car.py`（5261B）—— 循迹小车扩展板 I2C 协议（重点）

这是**本项目最有价值的资产之一**：完整还原了扩展板的寄存器级协议。

### 4.1 总线与地址

```python
i2c = I2C(1, scl=Pin(9), sda=Pin(8), freq=100000)
CAR_ADDR = 32        # 0x20  主控（电机）
# 扩展板第二片：CAR_ADDR + 1 = 33 = 0x21（ADC / RGB / RFID）

MOTOR_L = 0x20       # 左电机基址
MOTOR_R = 0x10       # 右电机基址
MOTOR_Z = 0x30       # 第三路（如云台 / 抬升）
```

> 与主控模块里的 `i2c_info_map = {'car': {'freq':100000,'sda':8,'scl':9}}` 完全吻合。

### 4.2 电机寄存器映射（以 `motor` 为基址）

| 偏移 | 写入长度 | 函数 | 含义 |
|---|---|---|---|
| `+0` | 4 字节 LE | `set_speed(motor, speed)` | 速度设定，范围 ±1024 |
| `+4` | 2 字节 LE | `set_power(motor, power)` | 功率设定，范围 ±1024 |
| `+8` | 4 字节 LE（读） | `get_position(motor)` | 编码器位置（有符号 32 位） |
| `+12` | 2 字节 LE | `set_ON_OFF(motor, mode)` | 使能 / 模式开关 |

### 4.3 位置闭环

```python
def position_pid_poll(motor, target_pos, vel):
    ...
    error = pos - target_pos
    # 限幅到 ±vel
    set_speed(motor, -error)
    if abs(error) < 30:
        set_speed(motor, 0)
        return True          # 到达
    return False

def demo_run_to(l, r, vel):
    position_mode()
    # 左右轮各自闭环，全部到位后返回
```

即扩展板内部执行速度环，`car.py` 在其上做一个**比例位置环**，
`demo_run_to(左目标, 右目标, 限速)` 可实现**定距离直行 / 精确转向**。

### 4.4 六路循迹 ADC

```python
def read_bottom_adc():
    data = i2c.readfrom_mem(CAR_ADDR + 1, 0, 12)
    line_sensors = [0] * 6
    for i in range(0, 6):
        line_sensors[i] = (data[i*2] + data[i*2+1]*256) >> 2
    return line_sensors
```

读 6 个 16 位值，`>>2` 转成 10 位（0-1023）。这就是"循迹小车"的传感器来源。

### 4.5 底部 RGB 与颜色识别

```python
def set_bottom_rgb(r, g, b):        # 注意写入顺序是 G, R, B
    data = bytearray(4); data[0]=g; data[1]=r; data[2]=b
    i2c.writeto_mem(CAR_ADDR+1, 0x10, data)

def demo_get_bottom_color():
    # 依次点亮 R/G/B 并采样第 6 路 ADC，做「反射光辨色」
```

### 4.6 RFID 读写

| 函数 | 寄存器 | 说明 |
|---|---|---|
| `Read_RFID_ID()` | `0x21+0x20+14` | 命令 1，查是否有卡；返回 True/False |
| `Read_RFID_bytes()` | `0x21+0x20+0..11` | 命令 2，读 12 字节卡内容 |
| `Write_RFID_bytes(content)` | `0x21+0x20+0..11` | 命令 3，写 12 字节（不足补空格），轮询完成位 |

命令寄存器约定：`0x20+12` = 长度，`0x20+14` = 命令/状态（0 表示完成）。

> 小结：`car.py` 覆盖了 **双电机 + 编码器 + 位置环 + 6 路循迹 + RGB 辨色 + RFID**，
> 是一份完整的竞赛小车驱动。

---

## 5. `sysfont.py`（8657B）—— 屏幕字体

```python
sysfont = {"Width": 5, "Height": 8, "Start": 0, "End": 254, "Data": bytearray([...])}
```

- 5×8 ASCII 点阵，`index = ASCII值 * 5`，每字节一列
- 恰好是 `ST7735.TFT.char()` 所要求的字体格式（`Start/End/Width/Height/Data`）
- 板子上 `sysfont.py`（源码）与 `sysfont.mpy`（编译版）**并存**，可自由修改

---

## 6. 传感器与执行器模块（COM11 独有）

相比 COM10（循迹小车），游戏机多出大量积木驱动：

| 模块 | 大小 | 功能 |
|---|---|---|
| `infraredDistanceSensorAlphaPiOne.mpy` | 249 | 红外测距 |
| `infraredSensorAlphaPiOne.mpy` | 232 | 红外传感器 |
| `infraredRemoteControlOne.mpy` | 736 | 红外遥控接收 |
| `ultrasonicSensorAlphaPiOne.mpy` | 822 | 超声波测距 |
| `temperatureAndHumiditySensorOne.mpy` | 375 | 温湿度 |
| `heartRateAndOxygenSensorOne.mpy` | 2055 | 心率血氧（配合 `max30102.mpy`） |
| `ledActuatorOne.mpy` | 2463 | LED 灯 |
| `ledLineActuatorOne.mpy` | 2551 | LED 灯带 |
| `steeringEngineActuatorAlphaPiOne.mpy` | 575 | 舵机 |
| `autoMotionOne.mpy` | 4274 | **电机运动控制**（`set_all_power` / `stop_motor` / `Update`） |
| `remoteControlSensorOne.mpy` | 915 | **摇杆 + 4 按键输入**（见 §6.1） |
| `car.py` | 5261 | **小车扩展板驱动**（源码） |

> COM10 有但 COM11 没有：`remoteControlActuatorOne.mpy`。

---

## 7. 资源文件

### 7.1 音频（13 个 `.dat`）

与 COM10 完全相同（alert / broken / drop / du / electric / funny / msg / pass /
record_start / record_end / right / tech / wrong）。

### 7.2 图片（`.htbmp`）

与 COM10 基本一致，**额外**多出车站主题素材：

| 文件 | 大小 | 推测 |
|---|---|---|
| `station_1.htbmp` | 5768 | 车站小图 |
| `station_4.htbmp` | 40968 | 车站大图（40KB，可能是全屏背景） |

### 7.3 未解资源 `r1.dat` / `r2.dat` / `r3.dat`

```
大小   180224 字节（176 KB）× 3
头部   \x80\x00 \x80\x00 \x80\x00 ...   （0x80/0x00 交替的规律位图）
```

- 三个文件大小完全相同，像是一组同级资源（3 关 / 3 曲 / 3 张图）
- 头部呈交替位模式，**不是**音频 PCM 的静音（应为全 0），更像**1bpp 位图或自定义编码**
- `ht_main.py` 未引用它们，`car.py` 也没有 → 可能是其它程序 / 历史遗留

**待确认**：需要把文件完整导出后分析（176KB × 3，串口导出约需数分钟）。

---

## 8. 与 COM10（循迹小车）的差异总览

| 维度 | COM10 循迹小车 | COM11 游戏机 |
|---|---|---|
| 固件性质 | 厂商定制（AlphaPi One） | **自编译通用固件** |
| 应用框架 | `controlBoardAlphaPiOne` | 同（模块文件相同） |
| 主程序 | 只开热点 `aiphapione` | **6 组广播遥控 + 电机动作** |
| 热点 | `aiphapione` / `12345678` | **`01` / `01`** |
| 小车驱动 | 无 `car.py` | **有，含 RFID / 循迹 / 位置环** |
| 传感器 | 少 | **多（超声波/红外/温湿度/心率）** |
| 字体源码 | 无 `sysfont.py` | **有** |
| 特殊资源 | 无 | **station_*.htbmp、r1~r3.dat** |
| 连接要求 | DTR 无关 | **必须 DTR=1** |

---

## 9. 硬件确认与控制链路

### 9.1 硬件：这就是一个摇杆手柄

用户观察「接的是摇杆、按键样式」——**经反汇编 + 实测完全证实**。

`remoteControlSensorOne.py`（版本 `v_2022_11_23`）反汇编还原：

```python
button_list = [13, 12, 11, 10]          # 4 个按键的 GPIO，PULL_UP，按下为低

def x_pos():              return 1023 - controlBoardAlphaPiOne.ReadAdc(8)
def y_pos():              return 1023 - controlBoardAlphaPiOne.ReadAdc(7)
def read_potentiometer(): return controlBoardAlphaPiOne.ReadAdc(6)

status_list = [0] * 15
```

| 部件 | 接口 | 说明 |
|---|---|---|
| 摇杆 X 轴 | **ADC GPIO8** | `1023 - ReadAdc(8)`，范围 0–1023 |
| 摇杆 Y 轴 | **ADC GPIO7** | `1023 - ReadAdc(7)`，范围 0–1023 |
| 电位器 | **ADC GPIO6** | 范围 0–1023 |
| 按键 ×4 | **GPIO 13 / 12 / 11 / 10** | `PULL_UP`，按下 = 低电平 |

**实测值**（摇杆居中、未按键）：

```
X = 534   Y = 531          ← 居中（理论中点 512）
POT = 674
status_list = [0,0,0,0, 532, 530, 0,0,0,0,0,0,0,0, 674]
```

### 9.2 `status_list` 索引表（`Update()` 填充）

| 索引 | 含义 | 判定条件 |
|---|---|---|
| 0–3 | 4 个按键 | `ReadPin(button_list[i], PULL_UP) == 0` |
| 4 | 摇杆 X | 0–1023 |
| 5 | 摇杆 Y | 0–1023 |
| 6 | **上** | `Y > 810` 且 `210 < X < 810` |
| 7 | **下** | `Y < 210` 且 `210 < X < 810` |
| 8 | **左** | `X < 210` 且 `210 < Y < 810` |
| 9 | **右** | `X > 810` 且 `210 < Y < 810` |
| 10 | 左上 | `Y > 810` 且 `X < 210` |
| 11 | 左下 | `Y < 210` 且 `X < 210` |
| 12 | 右上 | `Y > 810` 且 `X > 810` |
| 13 | 右下 | `Y < 210` 且 `X > 810` |
| 14 | 电位器 | 0–1023 |

> **方向阈值：`< 210` 或 `> 810`**，居中区间 `210–810` 视为不动作（天然死区，防抖）。
> 另有 `getStatus(index_d)` 可按索引取值（内部用 `DataStruct(index_d).IntValue()`）。

### 9.3 完整控制链路（系统的设计意图）

```
┌─────────────────────┐         Wi-Fi UDP 广播          ┌─────────────────────┐
│  手柄（COM11 硬件）  │  ──── broadcast("上") ────►      │  小车（另一个）      │
│  摇杆 X/Y + 4 按键   │        "下" / "左" / "右" / "停"  │  hasBroadcast(...)  │
│  remoteControlSensor │                                 │  autoMotionOne      │
│        One           │                                 │   .set_all_power()  │
└─────────────────────┘                                 └─────────────────────┘
```

两块板**必须连到同一个 Wi-Fi**（或同一个热点，例如 `01` / `01`），广播才能互通。

### 9.4 问题：COM11 上烧的是「接收端」程序

`ht_main.py` 的逻辑是：

```python
def Loop2():
    autoMotionOne.set_all_power(DataStruct(50), DataStruct(50))   # 驱动电机 → 接收端

def Loop2Trigger(first):
    while not controlBoardAlphaPiOne.hasBroadcast(DataStruct("上")):   # 等广播 → 接收端
        yield True
```

它用 `hasBroadcast`（**收**）而不是 `broadcast`（**发**），并且直接驱动电机
—— 这是**小车端**程序，被放在了**手柄**硬件上。

**所以手柄的摇杆和按键现在完全没被读取，板子在静默等待广播。**

### 9.5 让它作为手柄工作的办法

把下面的「手柄端程序」写到 COM11（覆盖 `ht_main.py`）：

```python
import variable, time
time.sleep_ms(1000)
import math, basic
from basic import DataStruct
import controlBoardAlphaPiOne
import remoteControlSensorOne

def Loop1():
    controlBoardAlphaPiOne.openHotspot(DataStruct("01"), DataStruct("01"))
    yield False

def Loop2():
    last = None
    while True:
        controlBoardAlphaPiOne.Update()
        remoteControlSensorOne.Update()
        st = remoteControlSensorOne.status_list
        if st[6]:      cur = "上"
        elif st[7]:    cur = "下"
        elif st[8]:    cur = "左"
        elif st[9]:    cur = "右"
        else:          cur = "停"
        if cur != last:
            controlBoardAlphaPiOne.broadcast(DataStruct(cur))
            last = cur
        yield True

loop1 = Loop1(); loop1HasNext = True
loop2 = Loop2(); loop2HasNext = True

def Start(static_buf):
    controlBoardAlphaPiOne.init()
    controlBoardAlphaPiOne.InitBackground_buf(static_buf)
    soundLoop = controlBoardAlphaPiOne.play_record_loop()
    while True:
        next(soundLoop)
        if loop1HasNext: loop1HasNext = next(loop1)
        if loop2HasNext: loop2HasNext = next(loop2)
```

配套的**小车端**程序就是当前的 `ht_main.py` 原样（`hasBroadcast` → `autoMotionOne`），
把它放到接了电机的另一块板上即可。

> 提示：先用手柄端程序验证摇杆——`remoteControlSensorOne.Update()` 后打印
> `status_list[4]` / `status_list[5]`，推动摇杆看数值是否在 0–1023 变化。

### 9.6 待确认

1. 手柄板上是否需要显示内容（`station_*.htbmp` 车站素材 + `sysfont.py` 字体暗示有 UI）？
2. `r1/r2/r3.dat`（各 176KB）是否为配套游戏的关卡/音频资源？
3. 你要控制的小车是哪一块板？（COM10 当前程序只开热点，也不发广播）

---

## 10. 实战：打砖块游戏（摇杆 + 按键）

> 这是把 COM11 从"小车接收端"改造成可玩游戏的一次完整实践。
> 源码保存在 `projects/breakout/breakout.py`，板上部署为 `game.py`，可直接复用与改造。

### 10.1 硬件映射

| 部件 | 读取方式 | 范围 |
|---|---|---|
| 摇杆 X | `status_list[4]` | 0–1023 |
| 摇杆 Y | `status_list[5]` | 0–1023 |
| 按键 A/B/C/D | `status_list[0..3]` | 按下为 1 |
| 电位器 | `status_list[14]` | 0–1023 |

挡板位置由摇杆 X 线性映射（`PAD_W = 34`）：

```python
pad_x = status_list[4] * (160 - PAD_W) // 1023
```

### 10.2 屏幕驱动 API（实机实测签名）

**重点：这套 ST7735 驱动的坐标是元组，不是分开的 x/y**，写错会直接抛
`TypeError: function takes N positional arguments`：

| 调用 | 说明 |
|---|---|
| `tft.fill(color)` | 全屏填充 |
| `tft.fillrect((x, y), (w, h), color)` | 实心矩形（挡板 / 砖块） |
| `tft.rect((x, y), (w, h), color)` | 矩形边框 |
| `tft.line((x1, y1), (x2, y2), color)` | 直线 |
| `tft.hline((x, y), length, color)` | 横线 |
| `tft.vline((x, y), length, color)` | 竖线 |
| `tft.pixel((x, y), color)` | 单像素 |
| `tft.circle((x, y), r, color)` / `tft.fillcircle(...)` | 圆 |
| `tft.text((x, y), s, color, font, size, nowrap)` | 文字（需字体对象） |

颜色常量挂在 `TFT` 对象上：
`t.RED` / `t.GREEN` / `t.BLUE` / `t.WHITE` / `t.YELLOW` / `t.CYAN` /
`t.PURPLE` / `t.GRAY` / `t.MAROON` / `t.FOREST` / `t.NAVY` / `t.BLACK`。

**文字有两个硬限制**（由 `showStringWithXY` 反汇编还原）：

```python
# controlBoardAlphaPiOne.showStringWithXY(x, y, s) 的实际实现
textzh((x, y), s, TFT.WHITE, sysfont_zh16)
```

1. **字体固定 16×16** → 一行最多 10 个字符（160 ÷ 16），提示语必须极短
2. **颜色固定白色**，无法自定义

因此 HUD 高度取 18px（16px 字 + 边距），结束提示用 `WIN` / `GAME OVER`。

其它封装：`showPointWithXY(x, y, rgb)`、`clearScreen()`、
`showString(s)`（配合 `screen_next_x/y` 自动换行的文本模式）。

### 10.3 游戏规则与实现要点

| 元素 | 参数 | 说明 |
|---|---|---|
| 砖块 | 5 列 × 4 行，30×10 px | 每行一色：红 / 黄 / 绿 / 青 |
| 挡板 | 34×5 px，y = 118 | 摇杆连续控制 |
| 球 | 半径 2 px，每帧 2 px | 60 fps 下约每秒穿屏一次 |
| 生命 | 3 条 | 漏球扣 1 条，归零显示 `GAME OVER` |
| 得分 | 打掉 1 块 +1 | 清空 20 块显示 `WIN` |

关键实现点：

- **只重绘变化区域**：球每帧"先擦旧位置、再画新位置"，挡板仅在坐标变化时擦画，
  避免全屏刷新（20MHz SPI 下全屏约需 16ms）
- **挡板命中位置决定反弹角**：`off = (bx - pad_x) * 4 // PAD_W - 2` 得到 −2..2 的水平分量，
  打边缘角度大、打中间接近垂直
- **按键边沿检测**：`if st[0] and not self.btn_a`，否则长按会连续触发
- **`step()` 自带结束保护**：`if self.over: return`，防止结束后被反复调用导致生命无限递减
  （这是实机测试中真实踩到的 bug：模拟 200 帧后 `lives` 掉到 −22）

### 10.4 部署与复用

源码 `projects/breakout/breakout.py`（本地）与板上 `game.py` 字节数一致，互为备份。

```powershell
# 首次部署，或改完后重新部署
python tools/repl_probe.py COM11 put projects/breakout/breakout.py game.py
python tools/repl_probe.py COM11 reset          # 必须复位，否则 sys.modules 里还是旧模块
```

启动游戏（在 REPL 里，或在 MobaXterm 中）：

```python
import controlBoardAlphaPiOne as c
c.init()
import game
game.Breakout().loop()      # 死循环，Ctrl-C 退出
```

想让游戏**开机自启**，把 `ht_main.py` 换成：

```python
import game


def Start(static_buf):
    game.run(static_buf)
```

原 `ht_main.py` 已备份在 `firmware/com11_20220912/rootfs/ht_main.py`，随时可还原。

### 10.5 想换游戏怎么改

这份代码可以直接当模板用：

- 改 `BRICK_COLS` / `BRICK_ROWS` / `BRICK_W` / `BRICK_H` 调砖块布局
- 改 `new_ball()` 里的 `dx` / `dy` 初值调球速
- 改 `PAD_W` 调难度
- 换贪吃蛇等其它玩法时，复用 §10.2 的绘图 API 与 §10.1 的输入映射即可

---

## 11. 附：COM11 启动与 REPL 日志

```
（DTR=1 且 RTS=0 时；串口终端配置见 §2.1.1）
Traceback (most recent call last):
  File "main.py", line 4, in <module>
  File "ht_main.py", line 163, in Start
  File "controlBoardAlphaPiOne.py", line 559, in Update
  File "controlBoardAlphaPiOne.py", line 100, in uart_read
KeyboardInterrupt:
MicroPython 8e2a5ed99-dirty on 2022-09-12; ESP32S3 module with ESP32S3
Type "help()" for more information.
>>>
```

主循环阻塞点在 `controlBoardAlphaPiOne.py:559` 的 `Update()`，进而卡在
`uart_read()`（即等待 N32 的 UART 应答）。`Ctrl-C` 可随时打断进入 REPL。
