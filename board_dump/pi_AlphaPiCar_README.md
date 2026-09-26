# AlphaPiCar —— AlphaPi-One 智能小车 · 网页遥控

树莓派上运行一个轻量网页服务，浏览器打开即可用**虚拟摇杆 + 按钮**控制小车。
服务把操作转成 UDP 报文发给小车主控板（ESP32-S3，跑 `remote_car.py`）。

## 架构

```
手机/电脑浏览器  ──HTTP──▶  树莓派 car_web.py (:8080)  ──UDP 广播:1000──▶  小车 ESP32 主控  ──I2C 0x20──▶  电机/夹爪
                              │
                    (也可在 PC 上运行同一份 car_web.py)
```

- 小车与树莓派**必须在同一局域网**（已连同一路由器）。
- 小车用 **STA 模式**接入路由，正常情况下地址形如 `192.168.1.16`（在串口日志 `WIFI STA: (...)` 里可见）。
- 网页服务默认向 **UDP 广播 `255.255.255.255:1000`** 发送，无需写死小车 IP；也可用 `--board` 指定。

## 文件

| 文件 | 说明 |
|---|---|
| `car_web.py` | 网页遥控服务（HTTP 服务 + 虚拟摇杆页面 + UDP 发送）。纯标准库，无第三方依赖。 |
| `car_remote_client.py` | 命令行遥控客户端（备用/调试）。 |
| `systemd/alphaipi-web.service` | 开机自启的服务单元。 |

## 使用方法

### 1. 服务（已由 systemd 托管，开机自启）

```bash
sudo systemctl status alphaipi-web
sudo systemctl restart alphaipi-web
journalctl -u alphaipi-web -f
```

### 2. 打开网页

在**与树莓派同一局域网**的手机/电脑浏览器访问：

```
http://<树莓派IP>:8080
```

树莓派 IP 可用 `hostname -I` 查询。

### 3. 手动运行（调试用）

```bash
cd /home/pi/Codes/AlphaPiCar
python3 car_web.py --port 8080                 # 广播模式
python3 car_web.py --board 192.168.1.16        # 指定小车 IP
```

### 4. 命令行遥控（调试用）

```bash
python3 car_remote_client.py 上            # 前进
python3 car_remote_client.py 停            # 停止
python3 car_remote_client.py --shell       # 交互
```

## 通信协议

向小车 UDP 端口 `1000` 发送 JSON：

```json
{"token": "", "message": "上", "value": "60"}
```

| message | value | 作用 |
|---|---|---|
| `上` / `下` / `左` / `右` | 速度 -100~100（可选） | 固定方向行驶 |
| `drive` | `"左轮,右轮"`（各 -100~100） | **比例驱动**（摇杆用） |
| `停` | — | 停止 |
| `开爪` / `合爪` | — | 夹爪张开 / 闭合 |
| `开灯` / `关灯` | — | 板载灯 |

> 若主控端设置了 `TOKEN`，此处 `token` 必须一致；默认空串。

## 网页功能

- **虚拟摇杆**：拖动 = 比例差速行驶，松手自动停（对应 `drive` 指令）。
- **速度滑块**：20~100。
- **按钮**：停 / 开爪 / 合爪 / 开灯 / 关灯 / 前进。
- **急停**大按钮。

## 故障排查

| 现象 | 排查 |
|---|---|
| 网页打不开 | 确认树莓派 IP、`systemctl status alphaipi-web`、防火墙 8080 |
| 网页能开但小车不动 | ① 小车是否上线（串口看 `WIFI STA: (...)`）② 是否同一局域网 ③ `journalctl -u alphaipi-web -f` |
| 爪子方向反了 | 修改小车端 `remote_car.py` 的 `开爪/合爪` 映射后复位小车 |
| 小车地址变了 | 路由器里做 DHCP 保留；或网页服务保持广播模式即可 |
