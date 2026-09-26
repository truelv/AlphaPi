# 固件 com10_20221028（第 2 代 · 循迹小车）

> **从实机 COM10 导出的板载文件（全量备份）**。配套文档：`docs/AlphaPi_循迹小车（COM10）分析报告.md`。

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
| 连接要求 | DTR 无关（用默认自动探测即可；`--dtr` 反而连不上） |
| 备份时间 | 2026-09-13（首次部分导出 12 文件） / **2026-09-24（全量备份 62 文件）** |

> ✅ **本目录已是全量备份**：2026-09-24 用 `mpremote` 把板载根目录 62 个文件**全部**递归导出到 `rootfs/`，
> 与板载 `os.listdir()` 逐文件核对，大小完全一致。之前 README 标注的"部分备份"已作废。
>
> 全量备份命令（板子需先**重新插拔 USB** 复位，否则串口不响应）：
> ```powershell
> python -m mpremote connect COM10 fs cp -r : ./firmware/com10_20221028/rootfs/
> ```
>
> 逐文件 **SHA256 校验清单**见同目录 `MANIFEST.md`（62 项，含文件名/大小/哈希，
> 并附复算命令，可用于日后核对本地副本是否被改动）。

---

## `rootfs/` — 板载文件（全量 · 62 个 · 约 797 KB）

### 分类统计

| 类别 | 数量 | 文件 |
|---|---|---|
| 启动链 / 运行脚本（`.py`） | 7 | `boot.py` `main.py` `ht_main.py` `variable.py` `music.py` `pen.py` `scan.py` |
| 编译模块（`.mpy`） | 9 | `controlBoardAlphaPiOne.mpy` `basic.mpy` `ST7735.mpy` `autoMotionOne.mpy` `remoteControlActuatorOne.mpy` `remoteControlSensorOne.mpy` `steeringEngineActuatorAlphaPiOne.mpy` `max30102.mpy` `sysfont.mpy` |
| 标记 / 文本 | 2 | `testok` `scan_out.txt` |
| 音频资源（`.dat`） | 13 | `alert` `broken` `drop` `du` `electric` `funny` `msg` `pass` `record_end` `record_start` `right` `tech` `wrong` |
| 字库 | 2 | `HZK16`（267616B） `gb2312`（83607B） |
| 图片 | 29 | `logo2.bmp` + 28 个 `.htbmp`（24×2568B，4×1448B） |

> 注：`scan.py` / `scan_out.txt` 是早期排查时遗留在板上的诊断脚本及其输出，非出厂文件，
> 全量备份一并将其保留以保证与板载状态完全一致。

### 完整清单（名称 · 大小 · 类别）

| 文件 | 大小 | 类别 | 说明 |
|---|---:|---|---|
| `boot.py` | 120 | py | 启动读 N32 寄存器 `0x00`，bit2/bit3 同置则 `import factory_reset`；分配 40KB `static_buf` |
| `main.py` | 43 | py | `import ht_main` + `ht_main.Start(static_buf)` |
| `ht_main.py` | 683 | py | **出厂程序**：开机 `sleep_ms(1000)` → `init()` → 开热点 `aiphapione`/`12345678`，主循环空转 |
| `variable.py` | 63 | py | `defaultVariable = DataStruct(0)` |
| `music.py` | 25 | py | 占位 `def Update(): return`（主控模块导入时自动重写） |
| `pen.py` | 25 | py | 同上 |
| `scan.py` | 1455 | py | 诊断脚本（遗留产物，非出厂） |
| `controlBoardAlphaPiOne.mpy` | 22339 | mpy | **主控模块**：绘图/图层/图表/音频/网络/蜂鸣器/GPIO，`v_2023_03_28` |
| `basic.mpy` | 3393 | mpy | `DataStruct` 动态类型运行时（30 方法），`v_2022_11_30` |
| `ST7735.mpy` | 8182 | mpy | 屏幕驱动（坐标用元组） |
| `autoMotionOne.mpy` | 4274 | mpy | 自动运动（预设动作） |
| `remoteControlActuatorOne.mpy` | 1769 | mpy | 遥控执行器 |
| `remoteControlSensorOne.mpy` | 915 | mpy | 遥控传感器 |
| `steeringEngineActuatorAlphaPiOne.mpy` | 597 | mpy | 舵机执行器 |
| `max30102.mpy` | 8333 | mpy | 心率血氧传感器 |
| `sysfont.mpy` | 2519 | mpy | ASCII 点阵字库 |
| `testok` | 2 | 标记 | 内容 `ok`，出厂测试标记 |
| `scan_out.txt` | 1267 | 文本 | 诊断输出（遗留产物） |
| `alert.dat` | 20782 | 音频 | |
| `broken.dat` | 44974 | 音频 | |
| `drop.dat` | 27694 | 音频 | |
| `du.dat` | 16322 | 音频 | |
| `electric.dat` | 37486 | 音频 | |
| `funny.dat` | 26542 | 音频 | |
| `msg.dat` | 17686 | 音频 | |
| `pass.dat` | 18478 | 音频 | |
| `record_end.dat` | 17686 | 音频 | |
| `record_start.dat` | 21428 | 音频 | |
| `right.dat` | 20782 | 音频 | |
| `tech.dat` | 29422 | 音频 | |
| `wrong.dat` | 24812 | 音频 | |
| `HZK16` | 267616 | 字库 | 16×16 汉字点阵 |
| `gb2312` | 83607 | 字库 | GB2312 码表 |
| `logo2.bmp` | 8694 | 图片 | 启动 logo |
| `anti_clockwise_1.htbmp` | 2568 | 图片 | 逆时针箭头 |
| `back_1.htbmp` | 2568 | 图片 | 后退 |
| `boy_1.htbmp` | 1448 | 图片 | 男孩 |
| `car_1.htbmp` | 2568 | 图片 | 小车 |
| `clockwise_1.htbmp` | 2568 | 图片 | 顺时针箭头 |
| `data_1.htbmp` | 2568 | 图片 | 数据图标 |
| `dipped_beam_1.htbmp` | 2568 | 图片 | 近光灯 |
| `forward_1.htbmp` | 2568 | 图片 | 前进 |
| `girl_1.htbmp` | 1448 | 图片 | 女孩 |
| `gold_1.htbmp` | 1448 | 图片 | 金子 |
| `happy_1.htbmp` | 2568 | 图片 | 表情-开心 |
| `heart_1.htbmp` | 2568 | 图片 | 心率图标 |
| `high_beam_1.htbmp` | 2568 | 图片 | 远光灯 |
| `humidity_1.htbmp` | 2568 | 图片 | 湿度图标 |
| `left_front_1.htbmp` | 2568 | 图片 | 左前 |
| `left_rear_1.htbmp` | 2568 | 图片 | 左后 |
| `likes_1.htbmp` | 2568 | 图片 | 点赞 |
| `record_1.htbmp` | 2568 | 图片 | 录音图标 |
| `right_1.htbmp` | 2568 | 图片 | 右 |
| `right_front_1.htbmp` | 2568 | 图片 | 右前 |
| `right_rear_1.htbmp` | 2568 | 图片 | 右后 |
| `sad_1.htbmp` | 2568 | 图片 | 表情-伤心 |
| `sensor_1.htbmp` | 2568 | 图片 | 传感器图标 |
| `sound_1.htbmp` | 2568 | 图片 | 声音图标 |
| `stone_1.htbmp` | 1448 | 图片 | 石头 |
| `temperature_1.htbmp` | 2568 | 图片 | 温度图标 |
| `time_1.htbmp` | 2568 | 图片 | 时间图标 |
| `wrong_1.htbmp` | 2568 | 图片 | 错误图标 |

---

## `disasm/` — 反汇编产物（基于上面 `.mpy`，仍有效）

| 文件 | 大小 | 说明 |
|---|---:|---|
| `controlBoardAlphaPiOne.mpy.txt` | 391KB | 主控模块反汇编（API 还原主要依据） |
| `ST7735.mpy.txt` | 157KB | 屏幕驱动反汇编 |
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
python -m mpremote connect COM10 fs ls            # 列出板载文件（已确认可达）
python tools/repl_probe.py COM10 info             # 系统信息 + 文件列表 + 模块版本
python tools/repl_probe.py COM10 run "import controlBoardAlphaPiOne as c; print(c.board_info())"
```
