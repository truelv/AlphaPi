# 手柄版遥控（ESP32-S3 手柄板）

拿手柄板直接遥控小车，**不需要电脑或手机**：摇杆推哪走哪，另有 4 个按键。

```
手柄板 remote_pad.py ──UDP :1000 广播──▶ ESP32 小车 ──I2C 0x20──▶ 电机/夹爪/灯
```

## 文件

| 文件 | 说明 |
|---|---|
| `remote_pad.py` | 手柄板固件：读摇杆/按键 → 发 UDP 指令 → 屏上显示状态 |
| `main_pad.py` | 开机自启入口（传到板上另存为 `main.py`） |
| `deploy_pad.py` | 一键烧写：把上面两个文件传到手柄板并复位 |

## 操作

| 手柄 | 发送 | 作用 |
|---|---|---|
| 摇杆（比例差速，约 12.5Hz 流式） | `drive` `"左轮,右轮"` | 推哪走哪，松手自动停 |
| 电位器 | — | 速度上限（20~100） |
| A / B | `开爪` / `合爪` | 夹爪张开 / 闭合 |
| C | `开灯` / `关灯`（切换） | 板载 WS2812 |
| D | `停` | 急停 |

屏上显示：小车在线、速度、方向、左右轮值、摇杆原始 `X/Y`、按键提示。

## 硬件映射（板载）

| 部件 | 引脚 |
|---|---|
| 摇杆 X / Y | `ADC8` / `ADC7`（中位约 532/530，**开机会自动标定**） |
| 电位器 | `ADC6` |
| 按键 A / B / C / D | `GPIO13` / `GPIO12` / `GPIO11` / `GPIO10`（PULL_UP，按下为 0） |
| 屏 | ST7735 160×128（SPI，由 `controlBoardAlphaPiOne` 初始化） |

## 安装

```powershell
# 一键：上传 remote_pad.py + main.py 并复位（默认 COM11，自动带 --dtr）
python projects/AlphaPiCar/host/pad/deploy_pad.py
python projects/AlphaPiCar/host/pad/deploy_pad.py COM11        # 指定串口
python projects/AlphaPiCar/host/pad/deploy_pad.py --no-reset   # 只上传不复位
```

手动方式：

```powershell
python tools/repl_probe.py COM11 put projects/AlphaPiCar/host/pad/remote_pad.py --dtr
python tools/repl_probe.py COM11 put projects/AlphaPiCar/host/pad/main_pad.py main.py --dtr
python tools/repl_probe.py COM11 reset --dtr
```

> ⚠️ COM11 是 ESP32-S3 原生 USB CDC，**务必加 `--dtr`**（DTR=1 / RTS=0）。
> 不加时工具的 DTR 自动探测可能误判并回退 `DTR=0`，导致通信中断、把板上文件写坏。

## 配置（`remote_pad.py` 顶部）

| 配置 | 默认 | 说明 |
|---|---|---|
| `WIFI_SSID` / `WIFI_PASSWORD` | TP-LINK_F18C | 与小车同一局域网（板上 `boot.py` 通常已连，这里是兜底） |
| `CAR_PORT` | 1000 | 小车监听端口 |
| `TOKEN` | `""` | 需与小车端一致 |
| `INVERT_X` / `INVERT_Y` | `False` | **方向反了就改这里**：推右却左转 → `INVERT_X`；推上却后退 → `INVERT_Y` |
| `DEADZONE` | 0.16 | 摇杆死区（防中位漂移导致车爬行） |
| `POT_MIN_SPD` / `POT_MAX_SPD` | 20 / 100 | 电位器映射的速度范围 |

## 调试

串口日志（**仅在输出变化时**打印）：

```
remote_pad wifi ip=192.168.1.15
remote_pad center x=532.2 y=530.2
remote_pad ready -> udp 255.255.255.255:1000
PAD x=532 y=532 pot=130 -> L+0 R+0 STOP
KEY A -> 开爪
```

```powershell
python tools/serial_log.py COM11 115200 8 --no-ctrl-c   # 看日志（别发 Ctrl-C，会打断程序）
python tools/pad_diag.py COM11 16                       # 复位 + 抓启动日志 + 检查 WiFi/模块/发送
```

## 排障

| 现象 | 排查 |
|---|---|
| 板上程序没起来 | `python tools/pad_diag.py COM11` 看是否有 Traceback |
| 小车完全不动 | ① 手柄屏上是否 `CAR ON`（收到小车心跳）② 两端是否同一局域网（看日志里的 IP） |
| 推杆方向反了 | 改 `INVERT_X` / `INVERT_Y`，再跑一次 `deploy_pad.py` |
| 松手后车还在滑一点点 | 正常：约 900ms 后失联保护会停车（也可按 `D` 急停） |
| 上传后 `FAILED` / 文件损坏 | 没加 `--dtr`；重跑 `deploy_pad.py` 并确认 `VERIFY OK` |
| 屏上没显示 | 不影响遥控（屏幕代码有容错）；先确认小车能收到指令 |

## 还原手柄板原固件

手柄板原本跑的是车控固件（仓库里已备份 `board_dump/com11/main.py`）：

```powershell
python tools/repl_probe.py COM11 put board_dump/com11/main.py main.py --dtr
python tools/repl_probe.py COM11 reset --dtr
```
