# AlphaPiCar —— AlphaPi-One 智能小车 · 网页遥控（树莓派）

本目录是部署在树莓派上的运行副本。浏览器打开即可用**虚拟摇杆 + 按钮**控制小车。

## 架构

```
手机/电脑浏览器 ──HTTP──▶ car_web.py (:8080) ──UDP 广播:1000──▶ 小车 ESP32 ──I2C 0x20──▶ 电机/夹爪
```

- 小车与树莓派必须在**同一局域网**。
- 小车用 STA 模式接入路由器（地址形如 `192.168.1.16`）。
- 服务默认向 UDP 广播 `255.255.255.255:1000` 发送；也可 `--board <IP>` 指定。

## 文件

| 文件 | 说明 |
|---|---|
| `car_web.py` | 网页遥控服务（HTTP + 虚拟摇杆 + UDP）。纯标准库。 |
| `car_remote_client.py` | 命令行遥控客户端（备用）。 |
| `systemd/alphaipi-web.service` | 开机自启单元。 |

## 使用

```bash
sudo systemctl status  alphaipi-web
sudo systemctl restart alphaipi-web
journalctl -u alphaipi-web -f
```

浏览器访问：`http://<树莓派IP>:8080`（用 `hostname -I` 查 IP）。

手动运行（调试）：

```bash
cd /home/pi/Codes/AlphaPiCar
python3 car_web.py --port 8080
```

## 协议

向小车 UDP `1000` 发 JSON：`{"token":"", "message":"上/下/左/右/停/开爪/合爪/开灯/关灯/drive", "value":"..."}`
（`drive` 的 value 为 `"左轮,右轮"`，用于摇杆比例驱动。）

## 关联文档（树莓派上的路径）

| 文档 | 说明 |
|---|---|
| [`../docs/lessons_learned.md`](../docs/lessons_learned.md) | 踩坑与经验总结（强烈建议先读） |
| [`../README.md`](../README.md) | `/home/pi/Codes` 项目索引 |

> 完整的项目源码与文档（含板端 `remote_car.py`）见 Windows 工作区仓库的 `projects/AlphaPiCar/`。
