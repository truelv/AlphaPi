# board —— 小车端固件（两条遥控路线共用）

把 AlphaPi-One 小车变成"无线受控端"：连 WiFi + 收 UDP 指令 + 驱动电机/夹爪/灯。

```
遥控端（网页 或 手柄）──UDP :1000──▶ remote_car.py ──I2C 0x20──▶ 电机 / 夹爪 / WS2812
```

> 这一份固件**只装一次**，网页版与手柄版都能控它（协议完全相同）。

## 文件

| 文件 | 说明 |
|---|---|
| `remote_car.py` | **主程序**：连网 + 收 UDP + 执行指令（含心跳 / 指令回执 / 失联自动停车） |
| `car_control.py` | 直接调用动作的示例库（`forward() / turn_left() / claw_close()`…），可在 REPL 里玩 |
| `main_remote.py` | 开机自启用的 `main.py`（内容即 `import remote_car` + `remote_car.main(static_buf)`） |
| `main_backup.py` | 板子原 `main.py` 备份（还原用） |

## 安装（一次性）

```powershell
python tools/upload_chunked.py projects/AlphaPiCar/board/remote_car.py
python tools/repl_probe.py COM10 put projects/AlphaPiCar/board/main_remote.py main.py
python tools/do_reset.py
```

手动方式：把 `remote_car.py` 传到板子根目录，`main.py` 改成

```python
import remote_car
remote_car.main(static_buf)      # static_buf 由 boot.py 提前分配，务必复用
```

## 配置（`remote_car.py` 顶部）

| 配置 | 默认 | 说明 |
|---|---|---|
| `MODE` | `"sta"` | `sta` = 连路由器进局域网（推荐）；`ap` = 自开热点 `AlphaPi01`（默认 `192.168.4.1`） |
| `WIFI_SSID` / `WIFI_PASSWORD` | — | STA 模式的 WiFi（当前：`TP-LINK_F18C`） |
| `TOKEN` | `""` | 设置后，遥控端 `token` 必须一致 |
| `DEFAULT_SPEED` | 50 | 方向指令不带 value 时的速度 |
| `AUTO_STOP_MS` | **900** | **失联自动停车**（>0，毫秒）；`0` = 锁存（收到"停"才停） |
| `HB_MS` | 2000 | 心跳广播间隔 |

> ⚠️ `AUTO_STOP_MS > 0` 要求遥控端**流式周期发送**（网页 150~200ms / 手柄 80ms）。
> 如果你自己写了"只在数值变化时才发"的客户端，需把 `AUTO_STOP_MS` 设为 `0`，
> 否则车会走一下停一下。

## 协议

见 [`../README.md`](../README.md#通信协议两套遥控端完全一致)。

## 说明

- **方向校准**：实车左右电机物理接线与逻辑相反，板端在 `_power()` 里做了**一次对调**
  （前进/后退不受影响，同时把左转/右转纠正过来）。换车/换电机后方向不对，改这一处。
- **爪子**是 Z 轴电机（功率 700），会一直转到限位；连续动作时留意发热。
- 板子原固件是自带循迹/游戏程序；本项目只替换 `main.py`，原文件已备份为 `main_backup.py`。
