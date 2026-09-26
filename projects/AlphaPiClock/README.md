# AlphaPiClock —— 量子兔（COM13）联网滚动时钟

> **目标硬件**：COM13 量子兔 AlphaPi（第 1 代，ESP32-C3）
> **用到的资源**：5×5 点阵 LED、3 个按键、14 颗 WS2812 灯带、N32 音频、WiFi / NTP
> **配套文档**：[`../../docs/AlphaPi_量子兔（COM13）分析报告.md`](<../../docs/AlphaPi_量子兔（COM13）分析报告.md>)

## 效果

上电后：

1. 联网 → NTP 对时（点阵上先滚一遍 `WiFi` → `SYNC`）
2. 进入主循环，点阵**滚动显示**当前时间 `12:34`
3. 灯带做**秒进度条**：14 颗灯随着秒数逐颗点亮，满 60 秒清零重来
4. **整点报时**：小时跳变时播放 `alert.dat`
5. 三个按键随时可用：

| 按键 | GPIO | 作用 |
|---|---|---|
| **A** | 10 | 切换显示模式：**时间 `HH:MM` → 日期 `MM-DD` → 星期 `MON`** |
| **B** | 20 | 强制重新 NTP 对时（离线时点阵显示 `oFF`） |
| **C** | 21 | 整点报时 开 / 关（点阵显示 `On` / `oFF`） |

没配 WiFi 时自动进入**离线模式**：从 `OFFLINE_START` 起走，功能其余部分完全一样。

## 目录结构

```
AlphaPiClock/
├── README.md                    # 本文
└── board/                       # 烧到板子上的文件
    ├── clock.py                 #   主程序（参数配置在文件顶部）
    ├── main.py                  #   开机自启入口：import clock; clock.run()
    ├── clock_secrets.example.py #   WiFi 凭据模板（入库）
    └── clock_secrets.py         #   真实凭据（⚠️ 被 .gitignore 忽略，不入库）
```

## 配置

### WiFi 凭据：单独一个文件，不入库

本仓库挂着**公开 remote**（`github.com/truelv/AlphaPi`），所以 `clock.py` 里**不写** WiFi 密码。
`clock.py` 顶部是这段自动加载逻辑：

```python
try:
    from clock_secrets import WIFI_SSID, WIFI_PASS
except ImportError:
    WIFI_SSID = ""
    WIFI_PASS = ""
```

凭据放在同目录的 `clock_secrets.py`，它被 `.gitignore` 的 `*_secrets.py` 规则忽略：

```powershell
# 从模板复制，再填真实值
Copy-Item projects/AlphaPiClock/board/clock_secrets.example.py `
          projects/AlphaPiClock/board/clock_secrets.py
```

```python
# clock_secrets.py
WIFI_SSID = "TP-LINK_XXXX"
WIFI_PASS = "your-wifi-password"
```

**找不到这个文件就自动进离线模式**，其余功能照常——所以别人 clone 下来不用改代码也能跑。

### 其它参数（都在 `clock.py` 顶部）

```python
TZ_HOURS  = 8                             # 时区（中国大陆 = 8）
NTP_HOST  = "ntp.aliyun.com"
NTP_RETRY = 3                             # NTP 重试次数
WIFI_TIMEOUT_S = 20                       # 联网超时（秒）

SCROLL_MS = 8000                          # 同一段文字重复滚动的间隔
CHIME_ON_HOUR = True                      # 整点报时
CHIME_FILE = "alert.dat"

USE_STRIP = True                          # 没接灯带就设 False
STRIP_PIN = 5                             # 灯带数据脚（固定 14 颗）
STRIP_BRIGHTNESS = 100                    # 0-100
STRIP_COLOR = 0x00B34D                    # 秒进度条颜色

BUTTON_ACTIVE_HIGH = True                 # 按键按下为高（固件用 PULL_DOWN）
OFFLINE_START = (2026, 9, 26, 12, 0, 0)   # 离线模式起始时间（本地时间）
```

## 部署

```powershell
# 0) 先关掉 MobaXterm / VS Code 等占用 COM13 的串口工具（串口独占）
#    COM13 是 USB-Serial/JTAG，不需要 --dtr

python tools/repl_probe.py COM13 put projects/AlphaPiClock/board/clock.py clock.py
python tools/repl_probe.py COM13 put projects/AlphaPiClock/board/main.py  main.py
python tools/repl_probe.py COM13 put projects/AlphaPiClock/board/clock_secrets.py clock_secrets.py   # 联网必需
python tools/repl_probe.py COM13 reset
```

`put` 会回读长度校验，输出里要有 `VERIFY OK`。
`reset` 之后板子重新执行 `boot.py` → `main.py`，直接进时钟。

预期启动日志：

```
MPY: soft reboot
[clock] boot: AlphaPi COM13 rolling clock
[clock] strip ready on GPIO5
[clock] connecting to <你的SSID> ...
[clock] wifi ok: ip=192.168.x.x gw=192.168.x.1 dns=114.114.114.114
[clock] ntp ok: 2026-09-26 20:31:07
```

离线模式下是：

```
[clock] no ssid configured -> offline mode
[clock] running offline
[clock] rtc set (offline): 2026-09-26 12:00:00
```

## 还原出厂 Demo

出厂程序是"人体红外 → 灯带点亮 + 播放 `r1.dat`"，已存档：

```powershell
python tools/repl_probe.py COM13 put firmware/com13_20220808/rootfs/main.py main.py
python tools/repl_probe.py COM13 rm clock.py
python tools/repl_probe.py COM13 reset
```

## 工作原理（几个关键设计决策）

### 1. 滚动显示用「异步」版本，不能用同步版

`control_board_v1` 有两个接口：

| 接口 | 行为 |
|---|---|
| `led_show_string(s)` | 把点阵字节写给 N32 后 **`sleep_ms(len*128)`** —— 显示 `12:34` 会阻塞 **3～4 秒** |
| `led_show_string_async(s)` | 只写不睡，**立即返回** |

**N32 自己负责滚动**：ESP32 一次性把整段（最多 10 个字符，5×5 字模 + `0x00` 间隔）
写进寄存器 `0x08`，之后由 N32 逐帧滚动。
所以时钟只需要"隔一段时间重刷一遍"，而不是自己逐列搬像素。

主循环不能被阻塞 3 秒（否则按键、音频全停），因此全程只用 async 版本：

```python
if t[4] != last_min or time.ticks_diff(time.ticks_ms(), last_show) > SCROLL_MS:
    last_min = t[4]
    show(text_for(mode, t))          # = cb.led_show_string_async(...)
    last_show = time.ticks_ms()
```

`SCROLL_MS` 就是"同一段文字隔多久重新滚一遍"。

### 2. 必须每帧喂音频泵

```python
sound_loop = cb.play_record_loop()   # 造一个生成器
while True:
    next(sound_loop)                 # 每帧喂一次，否则录音/播放全停
```

这是第 1 代固件的硬性要求（图形化积木运行时的形态）。整点报时用的
`cb.play("alert.dat")` 是同步实现，会阻塞约 0.6 秒，可接受。

### 3. 时区要自己加，离线要对时

- `ntptime.settime()` 写进 RTC 的是 **UTC**；本地时间要自己算：
  `time.localtime(time.time() + TZ_HOURS * 3600)`
- MicroPython 的 **epoch 是 2000-01-01**（不是 CPython 的 1970），
  `time.mktime` / `time.localtime` 都按 UTC 解释，
  所以离线模式写 RTC 时要先把"本地时间元组"换算成 UTC 元组：

```python
u = time.localtime(time.mktime((y, mo, d, h, mi, s, 0, 0)) - TZ_HOURS * 3600)
machine.RTC().datetime((u[0], u[1], u[2], u[6], u[3], u[4], u[5], 0))
```

- `machine.RTC().datetime()` **只接受元组**，传 epoch 整数会报
  `TypeError: object 'int' isn't a tuple or list`。

### 4. 联网后显式设 DNS

官方手册记录了 WiFi **DNS 解析失败（errno -202）** 的问题，规避办法是连上后重设 ifconfig：

```python
ip, mask, gw, _ = wlan.ifconfig()
wlan.ifconfig((ip, mask, gw, "114.114.114.114"))
```

### 5. 按键用边沿检测

`cb.UpdateButtonStatus()` 每帧刷新 `pa/pb/pc_last_status`（缓存的是**电平**）。
直接看电平会导致长按重复触发，所以在 `buttons_pressed()` 里做了一次
"当前为高 且 上次为低"的边沿判定，只返回**本次新按下**的按键。

按键是 `Pin.IN + PULL_DOWN`，**按下为高**（`BUTTON_ACTIVE_HIGH = True`）。

### 6. 灯带只在"格子数变化"时重画

`strip_tick(sec)` 把秒数映射成 `lit = sec * 14 // 60`。
`setPixelColor()` 内部每次都 `np.write()`，14 颗逐颗写一遍不便宜，
所以在 `lit` 没变时直接 return —— 实测每秒最多重画 1 次。

---

## 实机验证情况

已在实机 COM13 上验证（2026-09-26）：

| 项 | 结果 |
|---|---|
| 语法 / 上传 / 长度校验 | ✅ `VERIFY OK` |
| 灯带初始化（GPIO5，14 颗） | ✅ `strip ready on GPIO5` |
| 点阵滚动显示（`show("12:34")`） | ✅ 无异常返回 |
| 按键读取 | ✅ 返回 `[]`（未按下） |
| 离线模式 + 时区换算 | ✅ 得到 `2026-09-26 12:00:00 / SAT`（各字段均正确） |
| 开机自启 + 主循环持续运行 | ✅ `Ctrl-C` 调用栈停在 `run()` 主循环内的 `time.sleep_ms()` |
| **WiFi 连接** | ✅ `192.168.1.23 / 255.255.255.0 / gw 192.168.1.1 / dns 114.114.114.114` |
| **NTP 对时** | ✅ `ntp ok: 2026-09-26 14:56:06`，星期 `SAT` 正确 |
| 物理按键 / 显示观感 | ⏳ 需要人眼 + 手指确认 |

> 实测命令（把 REPL 从主循环里抢回来直接调函数，最可靠的验证方式）：
>
> ```powershell
> python tools/repl_probe.py COM13 run 'import sys; sys.modules.pop("clock", None); import clock; print(clock.wifi_connect()); print(clock.ntp_sync()); print(clock.local_now())'
> ```
>
> ```
> [clock] wifi already up: 192.168.1.23
> WIFI_CONNECT True
> [clock] ntp ok: 2026-09-26 14:56:06
> NTP_SYNC True
> LOCAL_NOW (2026, 9, 26, 14, 56, 6, 5, 269)
> ```
>
> 💡 **别用"开串口监听"来验证运行日志**：这块板子的 log 和 REPL 共用 USB-Serial/JTAG，
> 主机没打开端口时数据直接丢，而重新打开端口又不会复位板子 —— 中间的日志就永久丢了。
> 直接 `run` 调函数看返回值最稳。

## 排障

| 现象 | 原因 / 处理 |
|---|---|
| `PermissionError(13, '拒绝访问')` | 串口被别的程序占着（MobaXterm / VS Code / PuTTY），先关掉 |
| 上传成功但行为没变 | 忘了 `reset`。MicroPython 把已导入模块缓存在 `sys.modules` 里 |
| 连上 WiFi 但不显示对时成功 | 看日志里的 `ntp attempt N/3 failed`；换一个 `NTP_HOST` 或检查 DNS 设置 |
| 点阵不滚动 / 全黑 | 点阵由 N32 驱动；在 REPL 里先 `import control_board_v1 as cb; cb.led_show_string_async("HI")` 验证底层 |
| 灯带不亮 | 确认 `USE_STRIP=True` 且灯带接到了 GPIO5；日志里会有 `strip init failed` |
| 中文日志乱码 | Windows 控制台是 GBK，**日志只用 ASCII**（本工程已遵守） |

调试时可以在 REPL 里单独调函数，不用整份重跑：

```powershell
python tools/repl_probe.py COM13 run 'import sys; sys.modules.pop("clock", None); import clock; clock.set_rtc_offline(); print(clock.local_now()); clock.show("HI")'
```

## 下一步可以加

- 天气预报（`usocket` 手写 HTTP / `upip install urequests`，注意固件没内置 `urequests`）
- 番茄钟 / 倒计时模式（用 `cb.play()` 报时）
- 用加速度计做"翻转即切换显示"（`cb.IsForward()`）
- 把星期改成自定义缩写 / 加"秒"模式
