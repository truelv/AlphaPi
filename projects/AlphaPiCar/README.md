# AlphaPiCar —— AlphaPi-One 智能小车 · 网页遥控

把 AlphaPi-One（循迹小车）改造成**手机/电脑浏览器遥控**：
浏览器打开网页 → 虚拟摇杆 + 按钮 → UDP → 小车 ESP32 主控 → I2C 0x20 电机控制器 → 电机/夹爪/灯。

本项目同时给出**板端**程序与**上位机**程序，上位机可跑在 PC 或树莓派上。

## 架构

```
手机/电脑浏览器 ──HTTP──▶ car_web.py (:8080) ──UDP :1000──▶ ESP32 小车 ──I2C 0x20──▶ 电机/夹爪
                            (PC 或 树莓派)                      (remote_car.py)
```
- 小车与上位机**必须在同一局域网**。
- 小车用 **STA 模式**接入路由器（地址形如 `192.168.1.16`，串口日志 `WIFI STA: (...)` 可见）；
  也可切 **AP 模式**（小车自开热点 `AlphaPi01`，默认 `192.168.4.1`）。
- 上位机默认向 **UDP 广播 `255.255.255.255:1000`** 发送，无需写死小车 IP；也可 `--board <IP>` 指定。

## 目录

```
projects/AlphaPiCar/
├── README.md                  # 本文件
├── board/                     # 烧到 ESP32 小车上的板端程序
│   ├── remote_car.py          #   主程序：连网 + 收 UDP + 驱动电机/夹爪/灯
│   ├── car_control.py         #   直接调用动作的示例库（前进/转向/爪子…）
│   ├── main_remote.py         #   开机自启用的 main.py（替换板子 main.py）
│   └── main_backup.py         #   板子原 main.py 备份（用于还原）
├── host/                      # 跑在 PC / 树莓派上的上位机
│   ├── car_web.py             #   网页遥控服务（含虚拟摇杆、急停）·纯标准库
│   └── car_remote_client.py   #   命令行遥控客户端
└── deploy/                    # 树莓派部署资产
    ├── alphaipi-web.service   #   systemd 自启单元
    └── pi_Codes_README.md     #   /home/pi/Codes 顶层 README 模板
```

## 快速开始

### 1) 板端（一次性）

把 `board/remote_car.py` 传到板子根目录，并把板子 `main.py` 改成：

```python
import remote_car
remote_car.main(static_buf)      # static_buf 由 boot.py 提前分配，务必复用
```

> 部署/上传可用 [`tools/upload_chunked.py`](../../tools/upload_chunked.py)（分块，抗内存碎片）。
> 或直接编辑 `board/remote_car.py` 顶部的 `MODE / WIFI_SSID / WIFI_PASSWORD`。

### 2) 上位机 · 本机 PC（最简单）

```powershell
python projects/AlphaPiCar/host/car_web.py --port 8080
# 浏览器打开  http://<本机IP>:8080
```

### 3) 上位机 · 树莓派（常开，推荐长期）

见下文「部署到树莓派」。

### 4) 命令行遥控（调试）

```powershell
python projects/AlphaPiCar/host/car_remote_client.py 上
python projects/AlphaPiCar/host/car_remote_client.py --shell
python projects/AlphaPiCar/host/car_remote_client.py --ip 192.168.1.16 停
```

## 通信协议

向小车 UDP 端口 `1000` 发送 JSON：

```json
{"token": "", "message": "上", "value": "60"}
```

| message | value | 作用 |
|---|---|---|
| `上` `下` `左` `右` | 速度 -100~100（可选） | 定方向行驶 |
| `drive` | `"左轮,右轮"`（各 -100~100） | **比例驱动**（网页摇杆用） |
| `停` | — | 停车 |
| `开爪` / `合爪` | — | 夹爪张开 / 闭合 |
| `开灯` / `关灯` | — | 板载 WS2812 全亮白 / 熄灭 |

> 若板端设了 `TOKEN`，客户端 `token` 必须一致；默认空串。

## 网页功能

- **方向键**：前进 / 后退 / 左转 / 右转 / 停 —— **按住走、松手自动停**。
- **虚拟摇杆**：拖动 = 比例差速（前后 + 转向），松手自动停（对应 `drive`）。
- **速度滑块** 20~100；功能键：开爪 / 合爪 / 开灯 / 关灯；**急停**大按钮。
- **在线状态**：板子每 2s 广播心跳(`hb`)、每条指令回执(`ack`)；网页顶部显示
  「● 在线 / ● 信号弱 / ● 离线」三色（按心跳延迟 <2.5s / <5s / 超时），并显示板子 IP、
  心跳延迟、**最后指令**与当前速度。

> 树莓派上服务监听 UDP `1000`（<1024 特权端口），systemd 单元已加
> `AmbientCapabilities=CAP_NET_BIND_SERVICE` 授权；Windows 无此限制。

> 方向语义：`上=(+,+)`、`下=(-,-)`、`左`/`右`为原地转向。
> ⚠️ 板端已按**实车接线**在 `_power()` 内做过**左右对调校准**（左右电机物理接线与逻辑相反），
> 方向键与摇杆是同一套映射，因此两者方向一致；换车/换电机后如方向相反，改 `_power()` 一处即可。

## 部署到树莓派（systemd 自启）

```powershell
# 一键部署（paramiko）：上传代码 + 安装 systemd + 启动
python tools/deploy_pi.py
# 同步文档（含经验总结）到 /home/pi/Codes/docs/
python tools/deploy_docs.py
```

部署后目录：`/home/pi/Codes/AlphaPiCar/`（+ `/home/pi/Codes/docs/`）。运维：

```bash
sudo systemctl status  alphaipi-web
sudo systemctl restart alphaipi-web
journalctl -u alphaipi-web -f
```

## 关联文档

| 文档 | 说明 |
|---|---|
| [`docs/board_map.md`](../../docs/board_map.md) | 板子总线/引脚/电机控制器寄存器映射 |
| [`docs/lessons_learned.md`](../../docs/lessons_learned.md) | **踩坑与经验总结**（强烈建议先读） |
| [`docs/AlphaPi_循迹小车（COM10）分析报告.md`](<../../docs/AlphaPi_循迹小车（COM10）分析报告.md>) | COM10 实机取证与 API |
| [`docs/AlphaPi_实机调试指南.md`](<../../docs/AlphaPi_实机调试指南.md>) | 连板子、进 REPL、传文件 |
| [`tools/README.md`](../../tools/README.md) | 所有工具用法 |

## 排障速查

| 现象 | 排查 |
|---|---|
| 网页打不开 | 树莓派/PC 的 IP、`systemctl status alphaipi-web`、端口 8080 |
| 网页能开但车不动 | ① 小车是否上线（串口 `WIFI STA: (...)`）② 是否同一局域网 ③ 服务日志 |
| 改了代码没反应 | **必须复位板子**（`sys.modules` 缓存）；见 `docs/lessons_learned.md` |
| 爪子方向反了 | 改 `board/remote_car.py` 的 `开爪/合爪` 映射后复位 |
| 灯不亮 | 板端 `开灯` 需**真正设置像素颜色**（`SetBrightness` 只调亮度）|
