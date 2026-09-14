# AlphaPi 实机调试指南（COM10 / COM11 通用）

> **适用范围**：COM10（循迹小车，`VID_2F4E:PID_0102`）与 COM11（游戏机，`VID_303A:PID_4001`）
> **两块板通用**。
> 串口连接与 DTR 电平要求见 `AlphaPi_游戏机（COM11）分析报告.md` §2.1；本文讲**连上之后怎么用**。
> 整理日期：2026-09-13（基于实机复测）。

---

## 1. 前提：这是 MicroPython REPL，不是 shell

串口连上、按下 `Ctrl-C` 之后出现的 `>>>`，是 **MicroPython 的 Python 解释器提示符**，
不是 Unix shell。因此 `ls`、`ps`、`cd`、`cat`、`rm` 这些命令**全部不存在**——
你在这里敲的是 **Python 语句**，回车即执行。

好消息：shell 能干的事，用一两行 Python 都能做，只是写法不同（见 §3）。

> 两轮踩坑提醒（详见 `AlphaPi_游戏机（COM11）分析报告.md` §2.1）：
>
> 1. 串口终端的 **Flow control 必须设为 `None`**，否则收不到数据；
> 2. **COM11 必须 DTR=1 且 RTS=0**，且 DTR 不能在同一个句柄里翻转；
> 3. 连上后窗口是黑的**属于正常**——程序本身不打日志，必须敲 `Ctrl-C` 才出 `>>>`。

---

## 2. 终端按键

这是 REPL 真正的"命令集"，比任何字符串命令都重要。

| 按键             | 作用                                       | 说明                                                       |
| ---------------- | ------------------------------------------ | ---------------------------------------------------------- |
| **Ctrl-C** | 打断当前运行的程序，回到`>>>`            | 板子在`while True` 里静默运行时，唯一能"叫醒"它的手段    |
| **Ctrl-D** | 软复位，重新执行`boot.py` → `main.py` | 等价"重启"，写完文件后用它能立刻生效，不用拔插电源         |
| **Ctrl-E** | 进入**粘贴模式**                     | 写多行代码的唯一正确姿势，见 §4                           |
| **Ctrl-A** | 进入 raw REPL                              | 工具模式（本项目脚本用），提示`raw REPL; CTRL-B to exit` |
| **Ctrl-B** | 退出 raw REPL                              | 回到普通`>>>`                                            |
| **Tab**    | 补全                                       | `import os` 后敲 `os.<Tab>` 可列出成员                 |
| 上/下箭头        | 翻历史                                     | 视固件实现而定，部分版本不支持                             |

---

## 3. shell 命令 → REPL 写法对照

| 想做的事     | shell 写法      | 这个板子上要这么写                                                         |
| ------------ | --------------- | -------------------------------------------------------------------------- |
| 列文件       | `ls`          | `import os; os.listdir()`                                                |
| 详细列表     | `ls -l`       | `for f in sorted(os.listdir()): print('%-26s %8d' % (f, os.stat(f)[6]))` |
| 看文件内容   | `cat main.py` | `print(open('main.py').read())`                                          |
| 删文件       | `rm a.py`     | `import os; os.remove('a.py')`                                           |
| 看剩余空间   | `df -h`       | `import os; s = os.statvfs('/'); print(s[3] * s[0], 'bytes free')`       |
| 看总容量     | —              | `import esp; esp.flash_size()`                                           |
| 看内存       | `free`        | `import gc; gc.collect(); print(gc.mem_free())`                          |
| 看系统信息   | `uname -a`    | `import os; os.uname()`                                                  |
| 看支持的模块 | —              | `help('modules')`                                                        |
| 看进程       | `ps`          | **没有进程概念**：板上只有一条主执行流                               |
| 杀掉当前程序 | `kill`        | **Ctrl-C**                                                           |
| 重启         | `reboot`      | **Ctrl-D**                                                           |

**关于 `ps`**：MicroPython 没有多任务、没有进程表，整个板子只跑一条执行流
（`while True` 里那个生成器调度器）。"现在跑到哪了"的答案只能通过
`Ctrl-C` 触发的 Traceback 获得，见 §6。

---

## 4. Ctrl-E 粘贴模式（写多行代码的唯一正确姿势）

REPL 逐行执行，直接粘贴带缩进的多行代码（`def` / `for` / `while`）会乱套。正确步骤：

1. 敲 `Ctrl-E`，出现提示：
   `paste mode; Ctrl-C to cancel, Ctrl-D to finish`
2. 把整段代码粘进去（多行、带缩进都没问题）
3. 敲 `Ctrl-D` 结束，代码立即执行

示例：在终端里直接造一个文件并运行

```
Ctrl-E
f = open('hello.py', 'w')
f.write('print("hello from board")\n')
f.close()
import hello
Ctrl-D
```

> 小文件可以这样写；**整份程序不建议**——串口没有回显校验，粘贴几百行极易出错，
> 请用 §7 的文件传输方式。

---

## 5. 体检命令（复制即用）

在 `>>>` 后面逐行敲（每行回车）：

```python
import os; print(len(os.listdir()), 'files')            # 文件数
for f in sorted(os.listdir()): print(f)                 # 完整清单
import gc; gc.collect(); print('free', gc.mem_free())   # 剩余内存
import sys; print(sys.version)                          # 固件版本
help('modules')                                         # 可用模块列表（很长）
```

**COM11（游戏机）读摇杆与按键的实时状态**：

```python
import remoteControlSensorOne as r, controlBoardAlphaPiOne as c
c.init()
r.Update()
print(r.status_list)
```

`status_list` 索引含义：`0-3` = 四个按键，`4` = 摇杆 X，`5` = 摇杆 Y，
`6-13` = 上/下/左/右/左上/左下/右上/右下（阈值 `< 210` 或 `> 810`），`14` = 电位器。

实测（摇杆居中、未按键）：

```
joy_x 533  joy_y 918  pot 632     ← 该时刻摇杆被推在上方
buttons [0, 0, 0, 0]
```

**两块板的基础指标实测值**：

| 指标     | COM10（循迹小车）                        | COM11（游戏机）                           |
| -------- | ---------------------------------------- | ----------------------------------------- |
| 文件数   | 60                                       | 74                                        |
| 内存     | free 48528 / alloc 120432                | free 57152 / alloc 112512                 |
| 固件标识 | `AlphaPi One with ESP32S3`（厂商定制） | `ESP32S3 module with ESP32S3`（自编译） |

---

## 6. 获取"运行日志"的三个层次

**结论先行：这两块板的程序一行日志都不打。** `ht_main.py` 进入 `while True` 后彻底静默，
被动监听 5 秒收到 **0 字节是正常现象**。想看它在干什么，只有以下三个层次。

### 层次 1：Ctrl-C 打断，看它卡在哪（最接近"日志"的东西）

打断后会打印调用栈，这就是它的"运行状态快照"。两块板的卡点不同，很能说明问题：

```
# COM11（游戏机）
File "main.py", line 4, in <module>
File "ht_main.py", line 163, in Start
File "controlBoardAlphaPiOne.py", line 559, in Update
KeyboardInterrupt:
```

```
# COM10（循迹小车）
File "main.py", line 4, in <module>
File "ht_main.py", line 27, in Start
File "controlBoardAlphaPiOne.py", line 604, in Update
KeyboardInterrupt:
```

COM11 的 `Update()` 再往里会卡在 `uart_read()`——**在等 N32 协处理器的 UART 应答**。

### 层次 2：打断后手工调它的模块，观察状态

见 §5 的摇杆示例：把主循环停掉，自己逐帧调用模块，看传感器/状态量的真实数值。
这是排查硬件是否正常最快的手段。

### 层次 3：给程序加 print（真正的"上日志"）

需要改代码，见 §7。在目标位置插入 `print()` 后上传、软复位即可。

---

## 7. 开发与更新程序

### 7.1 方式 A：纯终端（不装任何东西）

用 §4 的 `Ctrl-E` 粘贴模式直接写文件。适合十几行以内的小试验。

### 7.2 方式 B：项目自带脚本（推荐，已实机验证）

**前提：先关掉串口终端会话**——串口独占，否则脚本会报
`PermissionError(13, '拒绝访问')`（见 §8）。

```powershell
cd d:\Codes\AlphaPi

# 1) 把板上原文件导回本地做备份
python tools/repl_probe.py COM11 get ht_main.py ./firmware/com11_20220912/rootfs/

# 2) 本地改好 ht_main.py ...

# 3) 上传覆盖（分块写入 + 自动长度校验）
python tools/repl_probe.py COM11 put ht_main.py

# 4) 软复位，让新代码生效（等价于终端里按 Ctrl-D）
python tools/repl_probe.py COM11 reset
```

其它动作：`ls`（列文件）、`cat 文件名`（打印内容）、`rm 文件名`（删除）、
`put 本地名 板载名`（另存为别的名字）、`run "python代码"`（直接执行一段代码）。

上传成功会回读长度做校验：

```
upload firmware/com11_20220912/rootfs/main.py -> _probe_tmp.py (43 bytes)
  board_size = 43 -> VERIFY OK
```

### 7.3 方式 C：官方 mpremote（最顺手，需自行安装）

```powershell
pip install mpremote
mpremote connect COM11 fs ls
mpremote connect COM11 fs cp ht_main.py :ht_main.py
mpremote connect COM11 repl
```

`mpremote` 是 MicroPython 官方工具，文件传输和 REPL 一条命令搞定，常玩建议装。

### 7.4 让改动生效（重要）

写完文件后在终端敲 **`Ctrl-D`**（或跑 `tools/repl_probe.py ... reset`），
板子会重新执行 `boot.py` → `main.py`。**不需要拔插电源。**

> **改完文件务必复位，否则可能完全看不到变化。** MicroPython 会把已导入的模块缓存在
> `sys.modules` 里，`import xxx` 不会重新读盘——文件明明改了，跑的却还是旧代码。
> （实机测试中曾因此白测一轮：修好一个 bug 后现象丝毫不变，复位后才生效。）
>
> 临时验证、不想复位时，也可以在 REPL 里手动清缓存：
>
> ```python
> import sys
> sys.modules.pop('game', None)   # 换成你自己的模块名
> ```

---

## 8. 串口独占规则（高频踩坑）

串口同一时刻**只能被一个程序打开**。打开失败时的表现与处理：

| 现象                                                    | 原因                                    | 处理                                                                          |
| ------------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------------------------- |
| `PermissionError(13, '拒绝访问')` / `Access denied` | 端口被别的程序占着                      | 关掉占用者：MobaXterm 的串口标签页、VS Code 串口监视器、PuTTY、Arduino IDE 等 |
| 终端里全黑无输出                                        | Flow control 不是`None`（RTS 被置位） | 改成`None`，见 `AlphaPi_游戏机（COM11）分析报告.md` §2.1.1                        |
| 终端里全黑无输出                                        | 程序本身静默                            | 敲`Ctrl-C`                                                                  |
| 之前能连、突然连不上                                    | DTR 被拉低过                            | 重新插拔 USB（DTR 在同一句柄内翻转不可恢复）                                  |

**关标签页 ≠ 关会话**：MobaXterm 里要确认串口会话真正断开，脚本才抢得到端口。

---

## 9. 两块板的差异与注意事项

| 维度     | COM10 循迹小车                                  | COM11 游戏机                                    |
| -------- | ----------------------------------------------- | ----------------------------------------------- |
| 固件     | 厂商定制（`AlphaPi One with ESP32S3`）内核 `25d2a8a04 on 2022-09-30`        | 自编译通用（`ESP32S3 module with ESP32S3`）内核 **1.19.1** / `8e2a5ed99-dirty on 2022-09-12`   |
| 主控模块 | `controlBoardAlphaPiOne.mpy`                  | 同                                              |
| 显示     | ST7735 TFT 160×128，SPI`sck41/mosi42/miso45` | 同                                              |
| 连接要求 | DTR 无关                                        | **必须 DTR=1 且 RTS=0**                   |
| 当前程序 | 只开热点 `aiphapione`（`ht_main.py` 683B）                          | **小车接收端**（`ht_main.py` 6312B），另有 `game.py`（打砖块，需手动启动） |
| 热点     | `aiphapione` / `12345678`                   | `01` / `01`                                 |

**注意事项**：

1. **COM10 的 `boot.py` 含恢复出厂逻辑**：启动时若读到特定按键组合会 `import factory_reset`。
   在 REPL 里不要去执行 `factory_reset`，也不要按住按键重启。
2. **不要混用两块板的假设**：引脚、硬件版本完全不同（详见
   `AlphaPi_循迹小车（COM10）分析报告.md` 与 `AlphaPi_游戏机（COM11）分析报告.md` 的对比表）。
3. **COM11 当前跑的是"小车接收端"程序**，它的摇杆和按键根本没被读取，
   所以它"作为游戏机"是没反应的——这是程序与硬件不匹配，不是故障。

---

## 10. 一页纸速查

```
连接：Serial 会话 / 115200 8N1 / Flow control = None
      COM11 额外要求 DTR=1 且 RTS=0
进入：连上后敲 Ctrl-C        → 出现 >>>

按键：Ctrl-C 打断    Ctrl-D 软复位    Ctrl-E 粘贴模式（Ctrl-D 结束）
      Ctrl-A 进 raw  Ctrl-B 退出 raw  Tab 补全

常用：
  import os; os.listdir()                                  列出文件
  print(open('main.py').read())                            看内容
  import gc; gc.collect(); print(gc.mem_free())            剩余内存
  import esp; esp.flash_size()                             总容量
  help('modules')                                          可用模块

日志：没有日志。Ctrl-C 的 Traceback 就是状态快照。
      COM11 卡在 controlBoardAlphaPiOne.py:559 (uart_read 等 N32)
      COM10 卡在 controlBoardAlphaPiOne.py:604

开发：python tools/repl_probe.py <PORT> get <文件> ./firmware/com10_20221028/rootfs/   备份
      本地改
      python tools/repl_probe.py <PORT> put <文件>                 上传
      python tools/repl_probe.py <PORT> reset                      生效
      ↑ 改完必须复位！否则 sys.modules 缓存里跑的还是旧代码
```

---

*本指南基于 2026-09-13 实机复测整理；两块板通用，端口差异处已单独标注。*
