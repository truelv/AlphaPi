# 网页版遥控（PC / 树莓派）

浏览器打开网页 → 虚拟摇杆 + 按钮 → UDP → 小车。

```
手机/电脑浏览器 ──HTTP──▶ car_web.py (:8080) ──UDP :1000 广播──▶ ESP32 小车
                          (PC 或 树莓派)
```

## 文件

| 文件 | 说明 |
|---|---|
| `car_web.py` | 网页遥控服务（HTTP 服务 + 虚拟摇杆 + 在线状态）。**纯标准库**，PC / 树莓派通用 |
| `car_remote_client.py` | 命令行遥控客户端（调试、或无浏览器时用） |
| `deploy/deploy_pi.py` | 一键部署到树莓派（上传代码 + 安装 systemd + 启动） |
| `deploy/alphaipi-web.service` | systemd 单元（含 `CAP_NET_BIND_SERVICE` 授权，可绑 1000 端口） |
| `deploy/pi_AlphaPiCar_README.md` | 部署到树莓派后的项目 README |
| `deploy/pi_Codes_README.md` | 树莓派 `/home/pi/Codes` 顶层 README 模板 |

## 用法

### 本机 PC（最简单）

```powershell
python projects/AlphaPiCar/host/web/car_web.py --port 8080
# 浏览器打开  http://<本机IP>:8080
```

### 树莓派（常开，推荐长期）

```powershell
python projects/AlphaPiCar/host/web/deploy/deploy_pi.py    # 一键部署
python tools/deploy_docs.py                                # 可选：同步文档到 /home/pi/Codes/docs/
```

部署后浏览器打开 `http://<树莓派IP>:8080`。运维：

```bash
sudo systemctl status  alphaipi-web
sudo systemctl restart alphaipi-web
journalctl -u alphaipi-web -f
```

### 命令行遥控（调试）

```powershell
python projects/AlphaPiCar/host/web/car_remote_client.py 上
python projects/AlphaPiCar/host/web/car_remote_client.py --shell
python projects/AlphaPiCar/host/web/car_remote_client.py --ip 192.168.1.16 停
```

## 网页功能

- **方向键**：前进 / 后退 / 左转 / 右转 / 停 —— **按住走、松手自动停**。
- **虚拟摇杆**：拖动 = 比例差速（前后 + 转向），松手自动停（对应 `drive`）。
- **速度滑块** 20~100；功能键：开爪 / 合爪 / 开灯 / 关灯；**急停**大按钮。
- **在线状态**：板子每 2s 广播心跳(`hb`)、每条指令回执(`ack`)；网页顶部显示
  「● 在线 / ● 信号弱 / ● 离线」三色（按心跳延迟 <2.5s / <5s / 超时），
  并显示板子 IP、心跳延迟、**最后指令**与当前速度。

> 树莓派上服务监听 UDP `1000`（<1024 是特权端口），systemd 单元已加
> `AmbientCapabilities=CAP_NET_BIND_SERVICE` 授权；Windows 无此限制。

## 排障

| 现象 | 排查 |
|---|---|
| 网页打不开 | 树莓派/PC 的 IP、`systemctl status alphaipi-web`、端口 8080 是否被占 |
| 网页能开但车不动 | ① 小车是否上线（小车串口打印 `WIFI STA: (...)`）② 是否同一局域网 ③ 服务日志 |
| 服务起不来（Linux） | 绑 1000 端口需要 `CAP_NET_BIND_SERVICE`，见 `deploy/alphaipi-web.service` |
| 状态显示"信号弱/离线" | 心跳延迟 >2.5s / >5s；检查 WiFi 距离与小车供电 |
