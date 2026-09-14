# 固件 com11_20220912（第 2 代 · 游戏机 / 摇杆手柄）

> **从实机 COM11 全量导出的板载文件系统**：75 个文件，1,425,684 字节。
> 配套文档：`docs/AlphaPi_游戏机（COM11）分析报告.md`。

## 实机标识

| 项目 | 值 |
|---|---|
| 串口 | COM11，`VID_303A:PID_4001`（**ESP32-S3 原生 USB CDC**） |
| Board 标识 | **`ESP32S3 module with ESP32S3`**（自编译通用固件） |
| MicroPython 内核 | **1.19.1** |
| 编译来源 | `8e2a5ed99-dirty on 2022-09-12`（`dirty` = 自行编译过） |
| 主控模块 | `controlBoardAlphaPiOne.mpy` → `v_2023_03_28` |
| 文件数 / 体积 | 75 个 / 1,425,684 字节（分区 6MB，已用 392×4096） |
| 连接要求 | **DTR=1 且 RTS=0**（详见分析报告 §2.1） |
| 备份时间 | 2026-09-13，`mpremote fs cp -r` 全量导出 |

> **注意**：`sys.version` 开头的 `3.4.0` 是 **Python 语言版本**，不是 MicroPython 内核版本；
> 内核版本看 `os.uname().release`。

---

## `rootfs/` — 完整文件系统（75 项）

### 启动链

| 文件 | 大小 | 说明 |
|---|---|---|
| `boot.py` | 168B | 通用 MicroPython 默认模板 + 一行 40KB `static_buf` |
| `main.py` | 43B | `import ht_main` + `ht_main.Start(static_buf)` |
| `ht_main.py` | **6312B** | **开机自启程序 = 小车接收端**：6 组「广播触发器 + 电机动作」 |

> 开机跑的是**小车接收端**程序（用 `hasBroadcast` 收、`autoMotionOne` 驱动电机），
> 摇杆和按键根本没被读取——所以这块板作为"游戏机"是没反应的。
> 本目录的 `ht_main.py` 是**原始版本**，可随时还原。

### 应用与驱动

| 文件 | 大小 | 说明 |
|---|---|---|
| `game.py` | 6272B | **打砖块游戏**（本次新增，需手动启动）→ 源码见 `projects/breakout/` |
| `car.py` | 5261B | 车扩展板 I2C 驱动：双电机 / 编码器 / 位置环 / 6 路循迹 ADC / RGB 辨色 / RFID |
| `controlBoardAlphaPiOne.mpy` | 22339B | 主控模块 |
| `basic.mpy` | 3393B | `DataStruct` 运行时 |
| `ST7735.mpy` | 8182B | 屏幕驱动 |
| `sysfont.py` | 8657B | 5×8 ASCII 点阵字体（源码，可改） |
| `sysfont.mpy` | 2519B | 同上，编译版（与源码并存） |
| `variable.py` | 63B | 全局变量容器 |
| `music.py` | 25B | 占位函数 |
| `pen.py` | 25B | 占位函数 |
| `testok` | 2B | 出厂测试标记 |

### 传感器 / 执行器积木（11 个 `.mpy`）

| 文件 | 功能 |
|---|---|
| `remoteControlSensorOne.mpy` | **摇杆 X/Y + 电位器 + 4 按键输入**（游戏机核心） |
| `autoMotionOne.mpy` | 电机运动控制（`set_all_power` / `stop_motor` / `Update`） |
| `max30102.mpy` | 心率血氧传感器底层 |
| `heartRateAndOxygenSensorOne.mpy` | 心率血氧积木 |
| `ultrasonicSensorAlphaPiOne.mpy` | 超声波测距 |
| `infraredDistanceSensorAlphaPiOne.mpy` | 红外测距 |
| `infraredSensorAlphaPiOne.mpy` | 红外传感器 |
| `infraredRemoteControlOne.mpy` | 红外遥控接收 |
| `temperatureAndHumiditySensorOne.mpy` | 温湿度 |
| `ledActuatorOne.mpy` | LED 灯 |
| `ledLineActuatorOne.mpy` | LED 灯带 |
| `steeringEngineActuatorAlphaPiOne.mpy` | 舵机 |

### 资源文件

| 文件 | 大小 | 说明 |
|---|---|---|
| `HZK16` | 267616B | 16×16 中文点阵字库 |
| `gb2312` | 83607B | GB2312 码表 |
| `station_1.htbmp` / `station_4.htbmp` | 5768 / 40968B | 车站主题图片（40KB 那张可能是全屏背景） |
| `logo2.bmp` | 8694B | 开机 logo |
| 约 30 个 `*_1.htbmp` | 1448–2568B | 方向箭头 / 车灯 / 表情 / 传感器图标等 |
| 13 个 `.dat` | 16–45KB | 音频（IMA ADPCM）：alert / broken / drop / du / electric / funny / msg / pass / record_start / record_end / right / tech / wrong |
| `r1.dat` / `r2.dat` / `r3.dat` | 各 180224B | **未解资源**，三个大小相同，头部呈 `\x80\x00` 交替位模式，疑似 1bpp 位图或自定义编码（待确认） |

---

## `disasm/` — 反汇编产物

| 文件 | 说明 |
|---|---|
| `remoteControlSensorOne.mpy.txt` | 摇杆/按键模块反汇编——还原了按键 GPIO（13/12/11/10）、摇杆 ADC（8/7）、电位器（6）与 `status_list` 索引语义 |

---

## 恢复方法

```powershell
# 全量导回板上（会覆盖板上同名文件）
python -m mpremote connect COM11 fs cp -r ./rootfs/ :

# 或单文件
python tools/repl_probe.py COM11 put rootfs/ht_main.py
python tools/repl_probe.py COM11 reset        # 复位后生效
```

> ⚠️ `r1/r2/r3.dat` 共 528KB，全量导回耗时较长，非必要可跳过。
