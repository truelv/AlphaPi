# AlphaPiCar —— AlphaPi-One 智能小车 · 无线遥控

把 AlphaPi-One（循迹小车 + 夹爪）改造成**无线遥控**，提供**两套互不影响、各自完整可用**的遥控端：

| 遥控端 | 运行设备 | 适合 |
|---|---|---|
| **网页版** [`host/web/`](host/web/) | PC / 树莓派 | 手机或电脑打开浏览器就能控；可常开、有在线状态与心跳 |
| **手柄版** [`host/pad/`](host/pad/) | 同族手柄板（ESP32-S3 + 摇杆） | 不依赖电脑/手机，拿起来就玩；比例摇杆手感最好 |

小车端固件只有一份 [`board/`](board/)，**两条路线共用**（两套遥控端发的是同一套 UDP 协议）。

## 架构

```
                    ┌── 网页版 ── 浏览器 ──HTTP──▶ car_web.py (:8080) ─┐
遥控端 ─────────────┤                                                  ├─ UDP :1000 广播 ─▶ ESP32 小车
                    └── 手柄版 ── 手柄板 ──(drive / 按键)──────────────┘                     │
                                                                      (remote_car.py) ── I2C 0x20 ──▶ 电机/夹爪/灯
```

- 小车与遥控端**必须在同一局域网**。小车用 **STA 模式**接入路由器（地址形如 `192.168.1.16`，
  串口日志 `WIFI STA: (...)` 可见）；也可切 **AP 模式**（小车自开热点 `AlphaPi01`，默认 `192.168.4.1`）。
- 遥控端默认向 **UDP 广播 `255.255.255.255:1000`** 发送，无需写死小车 IP。
- ⚠️ **同一时间只用一种遥控端**：两边都往同一端口发指令，同时用会互相抢控制权。

## 目录

```
projects/AlphaPiCar/
├── README.md                 # 本文件（总览）
├── board/                    # 【小车端固件】两条路线共用，只装一次
│   ├── README.md
│   ├── remote_car.py         #   主程序：连网 + 收 UDP + 驱动电机/夹爪/灯
│   ├── car_control.py        #   直接调用动作的示例库（前进/转向/爪子…）
│   ├── main_remote.py        #   开机自启用的 main.py（替换板子 main.py）
│   └── main_backup.py        #   板子原 main.py 备份（用于还原）
└── host/                     # 【遥控端】两套，各自独立完整
    ├── README.md             #   两者区别 / 如何选择
    ├── web/                  #   网页版
    │   ├── README.md
    │   ├── car_web.py        #     网页遥控服务（纯标准库）
    │   ├── car_remote_client.py   # 命令行遥控（调试用）
    │   └── deploy/           #     树莓派一键部署资产
    └── pad/                  #   手柄版
        ├── README.md
        ├── remote_pad.py     #     手柄板固件
        ├── main_pad.py       #     手柄板开机自启入口
        └── deploy_pad.py     #     一键烧写到手柄板
```

## 三步跑起来

```powershell
# 1) 小车端（一次性）—— 详见 board/README.md
python tools/upload_chunked.py projects/AlphaPiCar/board/remote_car.py
python tools/repl_probe.py COM10 put projects/AlphaPiCar/board/main_remote.py main.py
python tools/do_reset.py

# 2) 选一个遥控端（二选一；都装也行，用哪个开哪个）
python projects/AlphaPiCar/host/web/car_web.py --port 8080   # 网页版 → 浏览器开 http://<本机IP>:8080
python projects/AlphaPiCar/host/pad/deploy_pad.py            # 手柄版 → 一键烧到手柄板(COM11)
```

## 通信协议（两套遥控端完全一致）

**遥控端 → 小车**（UDP `1000`，JSON）：

```json
{"token": "", "message": "上", "value": "60"}
```

| message | value | 作用 |
|---|---|---|
| `上` `下` `左` `右` | 速度 -100~100（可选） | 定方向行驶 |
| `drive` | `"左轮,右轮"`（各 -100~100） | **比例驱动**（网页摇杆 / 手柄摇杆） |
| `停` | — | 停车 |
| `开爪` / `合爪` | — | 夹爪张开 / 闭合 |
| `开灯` / `关灯` | — | 板载 WS2812 全亮白 / 熄灭 |

**小车 → 遥控端**（同端口广播，用于显示在线状态）：

| message | value | 作用 |
|---|---|---|
| `hb` | 小车 IP | 心跳，每 2s 一次 |
| `ack` | 刚执行的指令 | 指令回执 |

> 若板端设了 `TOKEN`，遥控端 `token` 必须一致；默认空串。

方向语义：`上=(+,+)`、`下=(-,-)`、`左`/`右`为原地转向。

## 安全机制

- **失联自动停车**：`remote_car.py` 的 `AUTO_STOP_MS=900` —— 900ms 收不到指令就停车。
  两套遥控端都是**流式周期发送**（网页 150~200ms、手柄 80ms），所以断网、断电、走出范围会自动停下。
- **急停**：网页有急停大按钮；手柄有 `D` 键。
- **方向校准**：板端 `_power()` 内已按**实车接线**做过左右对调（左右电机物理接线与逻辑相反）。
  换车/换电机后方向若相反，改这一处即可。

## 关联文档

| 文档 | 说明 |
|---|---|
| [`host/README.md`](host/README.md) | **两套遥控端怎么选、怎么切换** |
| [`board/README.md`](board/README.md) | 小车端固件说明（配置项、安装、协议） |
| [`docs/board_map.md`](../../docs/board_map.md) | 板子总线/引脚/电机控制器寄存器映射 |
| [`docs/lessons_learned.md`](../../docs/lessons_learned.md) | **踩坑与经验总结**（强烈建议先读） |
| [`tools/README.md`](../../tools/README.md) | 串口 / REPL / 上传 / 反汇编 工具 |

## 排障速查

| 现象 | 排查 |
|---|---|
| 网页打不开 | 树莓派/PC 的 IP、`systemctl status alphaipi-web`、端口 8080 |
| 遥控端发了指令但车不动 | ① 小车是否上线 ② 是否同一局域网 ③ 是否**另一个遥控端也在发** |
| 改了代码没反应 | **必须复位板子**（`sys.modules` 缓存）；见 `docs/lessons_learned.md` |
| 爪子方向反了 | 改 `board/remote_car.py` 的 `开爪/合爪` 映射后复位 |
| 灯不亮 | 板端 `开灯` 需**真正设置像素颜色**（`SetBrightness` 只调亮度） |

---

> 📄 本仓库文档**只保存 Markdown**（不生成 HTML/PDF）。
