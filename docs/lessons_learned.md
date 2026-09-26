# AlphaPi-One 项目 · 踩坑与经验总结

> 适用范围：ESP32 / MicroPython 板卡逆向 + 机器人遥控 + 树莓派部署。
> 目的：把本项目踩过的坑固化成清单，**做下一个产品时直接照抄/避雷**。
> 每条格式：**现象 → 根因 → 解决**。

---

## 0. 十条最重要的（先看这个）

1. **打开串口 = 复位板子**。遥控运行时别开串口监视器；调试脚本也要考虑"一连就重启"。
2. **设备在两次会话之间不一定复位**，`sys.modules` 会缓存模块 → 改完代码**必须复位板子**（或 `sys.modules.pop("xxx")`）才生效。
3. **大文件/大代码不要一次性灌入**：串口桥缓冲会溢出、设备会 `MemoryError` → **分块**处理。
4. **base64 分块传输时每块各自补 `=`**，整体解码会在第一个 `=` 截断 → 必须**逐块解码再拼接**。
5. **大内存分配要趁早**：`bytearray(40960)` 在导入重模块后分配会失败 → 复用 `boot.py` 里提前分配的缓冲。
6. **MicroPython 是精简版**：`bytes` 没有 `.hex()`；`socket` 没有 `SO_BROADCAST`；`socket` 功能有限。
7. **先抓源码，再反编译**：设备上的 `.py` 往往自带注释/文档，比反汇编 `.mpy` 省事得多。
8. **寄存器寻址 = 智能外设**：能读写多个寄存器 + 有语义算法，就不是 PCF8574 那种简单 IO 扩展器。
9. **只读探测优先**：对未知 I2C 设备，先 `scan()` + `readfrom_mem()`；**不要贸然写寄存器**（可能直接驱动电机）。
10. **中文别直接 print 到 Windows 控制台**（GBK 报错）→ 用 `ascii + backslashreplace` 或写文件。

---

## 1. MicroPython / ESP32 板端（串口 / REPL / 内存）

| # | 现象 | 根因 | 解决 |
|---|---|---|---|
| 1.1 | 脚本长期 `NO_RAW` / `ALL_FAILED`，设备像"卡死" | 用错 RTS/DTR 触发了错误复位时序，把设备卡在 boot | **纯默认打开串口，绝不碰 DTR/RTS**；一次连接内多次重试进 raw REPL |
| 1.2 | 灌一大段代码后只收到 `OK` 或残缺输出 | 串口桥 TX 缓冲被"回显 + 输出"冲爆，数据丢失 | **分块慢发**（32 字节/块）+ 边发边丢弃回显 + 用 `START/END` 标记框住真正输出 |
| 1.3 | 上传新代码后行为没变化 | 设备**没复位**，模块被 `sys.modules` 缓存 | 复位板子；REPL 临时：`import sys; sys.modules.pop("模块名", None)` |
| 1.4 | `MemoryError: memory allocation failed` | 堆碎片化；导入重模块后再申请大块内存 | 大缓冲**尽早分配**（见 1.5）；或分块处理；`gc.collect()` |
| 1.5 | `bytearray(40960)` 偶发失败 | 同上 | **复用 `boot.py` 里已分配的 `static_buf`**（`getattr(__main__,"static_buf",None)`），别再 new 一份 |
| 1.6 | `'bytes' object has no attribute 'hex'` | MicroPython `bytes` 无 `.hex()` | 用 `ubinascii.hexlify(b).decode()` |
| 1.7 | `AttributeError: 'module' object has no attribute 'SO_BROADCAST'` | MicroPython `socket` 精简 | 不要设 `SO_BROADCAST`，直接 `sendto(广播地址)` |
| 1.8 | Windows 控制台打印中文报 `UnicodeEncodeError: 'gbk'` | 控制台是 GBK | 输出 `str(x).encode("ascii","backslashreplace").decode()`；或写文件再读 |
| 1.9 | 遥控中途打开串口监视器，车突然停了 | 开串口复位了板子 | 运行时**不要开**串口监视器 |
| 1.10 | 反汇编/上传脚本"时好时坏" | 进 raw REPL 依赖时序，有随机性 | 所有交互脚本**循环重试**，以标记/校验和确认成功 |

---

## 2. 通过串口拉取 / 上传文件（base64 over REPL）

| # | 现象 | 根因 | 解决 |
|---|---|---|---|
| 2.1 | 取大 `.mpy` 时设备报 `memory allocation failed` | 一次性 `b2a_base64(整文件)` 爆堆 | **分块**读取 + 每块单独 base64 打印 |
| 2.2 | 拼接后解码只得到第一块（512 字节） | **每块 base64 各自补了 `=`**，整体解码在第一个 `=` 处停止 | **逐行(逐块)解码再拼接字节**，不要整体解 |
| 2.3 | 上传大文件时编译报 `MemoryError` | 一条超长字符串常量编译需要连续内存 | **分块上传**：多次 raw-REPL 执行，`f=open(...)` 在 `__main__` 全局里跨块保持 |
| 2.4 | 上传"成功"但内容不对 | 没校验 | 上传后打印 `len(open(f,'rb').read())` 与本地比对 |
| 2.5 | 载荷里 `"\n"` 变成真换行导致语法错 | 宿主字符串转义 | 宿主里写 `"\\n"`（或严格用真换行，不在设备字符串里放 `\n`） |

---

## 3. `.mpy` 反编译

| # | 现象 | 根因 | 解决 |
|---|---|---|---|
| 3.1 | `mpy-tool.py` 报 `No module named 'makeqstrdata'` | 缺依赖 | 同时下载 `py/makeqstrdata.py` 放到同目录 |
| 3.2 | 不确定 `.mpy` 版本 | 版本在文件头 | 头 4 字节 `4d 06 ...`：byte0=`'M'`，**byte1=版本号**（本项目=6） |
| 3.3 | 想找函数签名/常量 | | `python mpy-tool.py -d x.mpy`，看 `simple_name:` 与 `args:`；常量看 `LOAD_CONST_SMALL_INT` |
| 3.4 | 反汇编很大看不过来 | | 先 `search` 关键字（`Pin`/`SPI`/`writeto`/寄存器偏移）再看上下文 |

---

## 4. 硬件逆向方法论（复用价值最高）

1. **Step 1 抓源码**：`os.listdir()` 列出设备文件；文本 `.py` 直接打印（自带注释=最好的文档）。
2. **Step 2 看导入图**：反汇编找 `IMPORT`/`children`，理清模块依赖。
3. **Step 3 总线测绘**：用 `machine.SoftI2C(任意GPIO)` 扫 I2C；SPI/UART 从固件里读引脚。
4. **Step 4 设备定性**：
   - 只响应 1 个"端口"、无寄存器 → **简单 IO 扩展器**（如 PCF8574）。
   - 能按寄存器读写、有算法语义（位置/PID/校验） → **智能外设/MCU**（本项目 0x20 = 电机控制器）。
5. **Step 5 只读探测**：`readfrom_mem(addr, reg, n)` 摸寄存器；**写之前先想清楚会不会驱动执行器**。
6. **Step 6 交叉验证**：固件里推断的寄存器/引脚，用实测（串口打印、发指令看反馈）确认。
7. **二分定位**：大段代码跑不动时，先跑最小片段，再逐段加回（本项目靠这招定位了 I2C `scan()` 卡死）。

---

## 5. 本车硬件最终速查（AlphaPi-One）

| 资源 | 结论 |
|---|---|
| 主控 | ESP32-S3，MicroPython，`.mpy` v6，主频 240MHz |
| **车体 UART** | UART1 @ **460800**，`TX=GPIO3`、`RX=GPIO0`（主状态协议 22 字节） |
| **车用 I2C** | SoftI2C `SCL=9, SDA=8` @100k；从机 **0x20 = 3 轴电机控制器** |
| 电机控制器寄存器 | 每电机一块：`+0x00` 速度(int32)、`+0x04` 功率(int16)、`+0x08` 位置(读)、`+0x0C` 模式(int16) |
| 电机基址 | `L=0x20`、`R=0x10`、`Z=0x30` |
| I2C 写校验 | 速度写入带 **4 字节取反校验**；位置读回带取反校验 |
| 电机控制 API | 模块 `autoMotionOne`：`set_all_power / set_speed / set_raw_power / stop_motor / set_claw / get_position / go_distance / turn_round` |
| 找不到 0x20 时 | 自动回退 **UART2 @38400**（`tx=8, rx=9`） |
| **SPI 屏(ST7735)** | 硬件 `SPI(2)` 20MHz：`SCK=41 MOSI=42 MISO=45 CS=40 DC=39 RST=38` |
| **WS2812 灯** | `autoMotionOne` 内建 `NeoPixel(Pin(7), 4)`（板载灯效） |
| 震动马达 | `WritePwm(4, v)` |
| 摇杆/按键 | 摇杆 `ADC 8(X)/7(Y)`、电位器 `ADC 6`；按键 `GPIO 10/11/12/13`（上拉低有效） |
| **⚠ 灯效坑** | `SetBrightness()` 只把亮度乘到**已有颜色**上；首次要能亮，必须**先 `setPixelColor()` 设颜色**，否则黑×亮=黑 |
| **⚠ 参数类型坑** | 库统一用 `basic.DataStruct` 传参；`packRGBd()` **返回 DataStruct**（别 `hex()` 它） |

---

## 6. 网络与远程控制

| # | 现象 | 根因 | 解决 |
|---|---|---|---|
| 6.1 | 板子热点在，但客户端拿不到 IP | / | 板子 `openHotspot` 自带 DHCP；客户端等待并重连即可 |
| 6.2 | 板子"自发自收"UDP 收不到 | `recv_udp` 前置条件：`ap_if.isconnected() or sta_if.isconnected()`；无真实客户端连接时直接返回 | **必须有真实客户端连上热点/STA 已连接**，端到端要真机测 |
| 6.3 | 板子自己给 `255.255.255.255` 发不回流 | lwIP 自广播不回环 | 自测用**本机 IP**或 `127.0.0.1`；对外用广播没问题 |
| 6.4 | PC 双网卡互相干扰 | 两张网卡都想当默认网关 | 一张上网、一张连设备；`netsh wlan connect ... interface="WLAN 2"`；配置文件要**按接口**添加 |
| 6.5 | 板子从 AP 改 STA 后热点消失 | `connectWifi` 会 `ap_if.active(False)` | 预期行为；STA 下板子进局域网，任何同网设备都能控 |
| 6.6 | 忘记板子 IP | DHCP 变动 | ① 用**广播** 255.255.255.255:1000（推荐）② 路由器做 DHCP 保留 ③ 串口日志 `WIFI STA: (...)` |
| 6.7 | 遥控长时间发指令但不动 | 丢包/顺序 | 方向指令**周期重发**（如 10Hz）+ 松手发"停"；或板端做**超时自动停**(`AUTO_STOP_MS`) |

**本项目通信协议**（UDP :1000，JSON）：
```json
{"token":"", "message":"上/下/左/右/停/开爪/合爪/开灯/关灯/drive", "value":"..."}
```
- `drive` 的 value=`"左轮,右轮"`（各 -100~100）→ 摇杆**比例驱动**。

---

## 7. 部署与运维

| # | 现象 | 根因 | 解决 |
|---|---|---|---|
| 7.1 | Windows 挂载盘看不到刚部署的文件 | **SMB 目录缓存**；且 `/home/pi` 是 `700` | 资源管理器 **F5** / 重开窗口；`net use Y: /delete` 后重连；确保用 **pi 账号**挂载 |
| 7.2 | `netsh wlan` 提示 "no profile assigned to interface" | 配置文件是**按接口**的 | `netsh wlan add profile filename=... interface="WLAN 2" user=all` |
| 7.3 | 自动化 SSH 到树莓派（无 sshpass） | Windows 没 sshpass | 用 **Python `paramiko`**：`pip install paramiko`；sudo 用 `echo 密码 \| sudo -S cmd` |
| 7.4 | 服务要开机自启/常驻 | | 写 **systemd** 单元到 `/etc/systemd/system/`，`systemctl enable --now` |
| 7.5 | 树莓派跑脚本依赖第三方库 | | 优先用**纯标准库**（本项目 `car_web.py` 零依赖，PC/Pi 通用） |
| 7.6 | 多项目混乱 | 无规范 | 约定：`/home/pi/Codes/<项目>/`+`README.md`+`systemd/`；顶层 `README.md` 做索引 |

---

## 8. 通用工程原则（做下一个产品时）

1. **最小可验证链路优先**：先把"能进 REPL"→"能读一个寄存器"→"能控一个动作"逐级打通，再叠加。
2. **每一步都留证据**：串口打印、`CMD` 回显、读回校验和——不要凭"应该可以"。
3. **改完必验证**：上传后校验大小；改行为后跑一次实测。
4. **隔离变量**：一次只改一个地方；二分法定位卡点。
5. **安全边界**：未知设备**先读后写**；执行器（电机/夹爪）操作限速、限时、可急停。
6. **协议要冗余**：UDP 不可靠场合 → 周期重发 + 死区(dead-man)自动停 + 参数带校验。
7. **文档即交付**：项目自带 README（架构/协议/用法/排障）+ 顶层索引；踩坑单独成文。
8. **服务化思维**：常驻能力用 systemd；配置（SSID/密码/端口）集中到文件顶部易改。
9. **零依赖优先**：能标准库解决就不引第三方，跨平台部署最省心。
10. **代码按项目分类**，不堆在一个目录里；本文件就是"跨项目经验库"。

---

## 9. 本项目沉淀的可复用工具（`board_dump/`）

| 脚本 | 作用 | 复用场景 |
|---|---|---|
| `scan_only.py` | raw-REPL 跑一段代码并抓输出 | 板子任意即席探查 |
| `dump_src.py` / `decode_mpy.py` | 拉取设备文件；`.mpy` 分块 base64 取回并解码 | 逆向任何 MicroPython 板 |
| `repl_eval.py` | 在板子 REPL 运行本地 `.py` 片段 | 快速验证想法 |
| `upload_file.py` / `upload_chunked.py` | 上传文件到板子（含分块版） | 部署板端脚本 |
| `mpy-tool.py`(+`makeqstrdata.py`) | 官方 `.mpy` 反汇编 | 看编译模块的签名/常量 |
| `probe_car.py` | 只读探测 I2C 外设寄存器 | 摸清任何 I2C 智能外设 |
| `deploy_pi.py` | paramiko 部署到树莓派 + 装 systemd | 树莓派批量部署 |
| `car_web.py` | 零依赖网页遥控（虚拟摇杆） | 任何"HTTP→UDP/串口"控制面板 |

产品侧代码：

| 文件 | 位置 | 说明 |
|---|---|---|
| `remote_car.py` | 板子 `/` | 板端：连 WiFi(STA/AP) + 收 UDP + 驱动电机/爪子/灯 |
| `car_web.py` | PC & 树莓派 | 网页遥控服务（含虚拟摇杆、急停） |
| `car_remote_client.py` | PC & 树莓派 | 命令行遥控 |
| `/home/pi/Codes/AlphaPiCar/` | 树莓派 | 项目目录（README + systemd 自启） |

---

## 10. 做"下一个产品"的 Checklist（照抄即可）

- [ ] **板端**
  - [ ] 复用 `boot.py` 的 `static_buf`，不自己 new 大内存
  - [ ] 配置项（WiFi/端口/token/速度）集中到文件顶部
  - [ ] 关键动作打日志（`CMD xxx`），便于无屏调试
  - [ ] 加**死区/超时自动停**，防失控
  - [ ] 模块更新后**复位板子**（或清 `sys.modules`）
- [ ] **上位机**
  - [ ] 优先**广播**发指令，别写死设备 IP
  - [ ] 松手/断开自动发"停"
  - [ ] 网页端做**急停**大按钮 + 触摸友好
- [ ] **部署**
  - [ ] 代码放 `/home/pi/Codes/<项目>/`，带 `README.md`
  - [ ] systemd 单元 + `enable --now`
  - [ ] 顶层 `README.md` 更新索引
  - [ ] 用**纯标准库**，减少依赖
- [ ] **文档**
  - [ ] 项目 README：架构图 / 协议表 / 用法 / 排障
  - [ ] 把新踩的坑补进本文件（跨项目经验库）
- [ ] **逆向新板子时**
  - [ ] 先 `os.listdir()` + 读 `.py` 源码
  - [ ] 再 `.mpy` 反汇编；`SoftI2C` 扫总线；**先读后写**
  - [ ] 设备定性：简单 IO 扩展器 vs 智能外设
