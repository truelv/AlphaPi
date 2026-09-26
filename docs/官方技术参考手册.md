# 参考资料

| 文件 | 说明 |
|---|---|
| `AlphaPi_One_技术参考手册_v4.pdf` | 官方技术参考手册。正文标题为 v3（2026-08-28），文末追加 v4 新章节 |

---

## 手册要点摘录

### 三种固件状态（手册 v4 新增章节）

| 特性 | 原板（定制固件） | 通用版（MicroPython） | 小智固件（AI 助手） |
|---|---|---|---|
| 开发语言 | MicroPython | MicroPython | C++ / ESP-IDF |
| 屏幕 | ST7735.mpy | 需自行实现 | ST7789 + LVGL9 |
| 中文显示 | HZK16 + `textzh` | 需自行实现 | Noto Sans |
| 音频 | .dat / .wav / .ima | 仅 16kHz PCM | Opus + N32 |
| 语音识别 | ✗ | ✗ | WakeNet9 + MultiNet5 |
| AI 对话 | ✗ | ✗ | ✓ |
| HTTPS | ✗ | `ssl` + `urequests` | mbedTLS |
| OTA | ✗ | ✗ | 双分区 OTA |
| DataStruct | 必需 | 不需要 | N/A |
| 音频波特率 | 460929 | 460929 | 1 Mbps |

### N32 协处理器寄存器表（手册 §6.4）

| 地址 | 名称 | 读写 | 说明 |
|---|---|---|---|
| `0x00` | KEY | 读 | 按键状态，A 键 = bit2（`0x04`） |
| `0x10` | AUDIO_CTRL | 写 | 录音控制：1 = 开，0 = 关 |
| `0x11` | AUDIO_READ | 读 | 读取麦克风 PCM |
| `0x12` | — | 读 | 固件 `read_volume()` 实际读的地址 |
| `0x14` | VOLUME | 写 | 音量 0–100 |
| `0x15` | AUDIO_STREAM | 写 | 音频流写入（播放），每块 200 字节 |

### 音频参数

- 16kHz / 16-bit signed little-endian / mono PCM
- 每块 200 字节 = 100 样本 = 6.25ms
- **播放前必须停录**（半双工）

### 另一款 12864 LCD 子板（手册 v4 附录）

| 项目 | 参数 |
|---|---|
| LCD | LX-12864L，ST7565 兼容，SPI，128×64，2.0 寸 |
| 显示结构 | 16 字符 × 4 行（8×16 点阵） |
| MCU | N32G031F8S7（I2C 从机 + SPI 主控） |
| I2C 从机地址 | `0x09` |
| I2C 引脚 | SCL = GPIO5，SDA = GPIO4（即早期文档里"未知"的 P1 / P2） |
| I2C 速率 | ≤50kHz（每次发送后需延时 0.03s） |

手册附有完整驱动 `walnut_lcd.py`（`WalnutLCD` 类：`show` / `icon` / `flip`）。

### 常见问题速查

- **WiFi DNS 失败（-202）**：需手动 `wlan.ifconfig((ip, mask, gw, '114.114.114.114'))`
- **通用版无 MP3 解码器**：网络收音机需换 Arduino + ESP32-audioI2S
- **小智固件白屏**：其帧缓冲为 320×240，需调 offset 适配 128×160 屏幕
- **原板 TFT 报参数错误**：底层 TFT API 需用 `DataStruct` 包装参数

---

> 完整分析见 `../docs/AlphaPi_项目分析文档.md` §12。
> 注意：手册描述的是**通用规格**，具体到手上这块板子请以
> `../docs/` 下的实机分析报告为准。
