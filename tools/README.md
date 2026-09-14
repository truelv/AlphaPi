# 工具

串口通信、REPL 操作与固件反汇编的配套脚本。

| 工具 | 用途 |
|---|---|
| `serial_log.py` | 串口日志查看 / 监听 |
| `repl_probe.py` | 通过 raw REPL 读写板子：内省、列文件、传文件、执行代码、软复位 |
| `usb_probe.py` | 轮询四种 DTR/RTS 组合，验证设备的电平要求 |
| `mpy-tool.py` | MicroPython 官方 `.mpy` 反汇编工具（v1.19.1） |
| `makeqstrdata.py` | `mpy-tool.py` 的依赖脚本 |

依赖：

```powershell
pip install pyserial        # 必需
pip install mpremote        # 可选，官方工具，递归导出很方便
```

---

## serial_log.py

看串口输出。

```powershell
python tools/serial_log.py COM11 115200 5          # 看 5 秒（默认会发 Ctrl-C 打断程序）
python tools/serial_log.py COM11 115200 --follow   # 持续监听，Ctrl-C 退出
python tools/serial_log.py COM10 115200 8 --no-ctrl-c   # 只被动监听，不发任何数据
python tools/serial_log.py COM10 115200 8 --hex         # 额外打印十六进制
python tools/serial_log.py COM10 115200 8 --no-dtr      # 需要 DTR=0 的设备
```

| 参数 / 开关 | 说明 |
|---|---|
| `端口 波特率 秒数` | 位置参数，均有默认值 |
| `--follow` | 一直监听直到手动中断 |
| `--no-ctrl-c` | 不发送 Ctrl-C（纯被动监听） |
| `--hex` | 同时打印十六进制 |
| `--no-dtr` | 把 DTR 拉低（**默认是置位**，因为 COM11 需要 DTR=1） |

---

## repl_probe.py

读写板子文件系统、执行任意代码。

```powershell
python tools/repl_probe.py COM11 info               # 系统信息 + 文件列表 + 模块版本
python tools/repl_probe.py COM11 ls                 # 列出板上文件
python tools/repl_probe.py COM11 cat boot.py        # 打印文件内容
python tools/repl_probe.py COM11 get boot.py ./x/   # 导出到本地目录
python tools/repl_probe.py COM11 put x.py           # 上传（覆盖同名文件）
python tools/repl_probe.py COM11 put x.py y.py      # 上传并另存为 y.py
python tools/repl_probe.py COM11 rm y.py            # 删除板上文件
python tools/repl_probe.py COM11 run "print(1+1)"   # 执行一段代码
python tools/repl_probe.py COM11 reset              # 软复位（让新写入的代码生效）
```

| 动作 | 说明 |
|---|---|
| `info` | 系统版本 / 平台 / 文件清单 / 内存 / Flash / 模块版本 |
| `ls [路径]` | 列文件（含大小） |
| `cat <文件>` | 打印文件内容到本地 stdout |
| `get <文件> [目录]` | 分块导出到本地，默认 `./board_dump/` |
| `put <本地文件> [板载名]` | 分块上传，写完自动回读长度校验 |
| `rm <文件>` | 删除 |
| `run "<代码>"` | 在 raw REPL 中执行 |
| `reset` | 发 Ctrl-D 软复位，重新执行 `boot.py` → `main.py` |

> **DTR 会自动处理**，不需要手动加参数。对需要 DTR=1 的设备（COM11）会自动适配。

---

## usb_probe.py

当某个设备串口无输出时，用这个确认它到底需要什么电平：

```powershell
python tools/usb_probe.py COM11 2
```

输出示例（COM11 实测）：

```
[DTR=1 RTS=0] 325 bytes   ← 唯一有输出的组合
[DTR=0 RTS=1] 0 bytes
[DTR=1 RTS=1] 12 bytes
[DTR=0 RTS=0] 0 bytes
```

---

## mpy-tool.py

反汇编 `.mpy` 编译模块：

```powershell
python tools/mpy-tool.py -d firmware/com11_20220912/rootfs/basic.mpy > basic.mpy.txt
```

已有反汇编产物的位置：各固件目录下的 `disasm/`。

---

## 另一条路：mpremote（官方工具）

递归导出/还原整块文件系统时比 `repl_probe.py` 快得多：

```powershell
python -m mpremote connect COM11 fs ls                    # 列文件
python -m mpremote connect COM11 fs cp -r : ./backup/     # 全量导出
python -m mpremote connect COM11 fs cp -r ./rootfs/ :     # 全量导回
python -m mpremote connect COM11 repl                     # 直接进 REPL
```

---

## ⚠️ 使用注意

1. **串口独占**：同一时刻一个串口只能被一个程序打开。用这些脚本前，
   先关掉 MobaXterm 的串口会话，否则会报 `PermissionError(13, '拒绝访问')`。
2. **改完文件必须复位**：MicroPython 把已导入模块缓存在 `sys.modules` 里，
   `put` 之后不 `reset` 的话，跑的仍是旧代码。
3. **DTR 不能在同一个句柄里翻转**：一旦拉低再拉高，往往要重新插拔 USB 才能恢复。

完整用法与踩坑记录见 `docs/AlphaPi_实机调试指南.md`。
