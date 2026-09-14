# 板上项目

本目录存放**跑在板子上的应用 / 游戏**，一个项目一个子目录。

| 项目 | 目标板 | 说明 |
|---|---|---|
| [`breakout/`](breakout/) | COM11（游戏机） | 打砖块游戏，摇杆控制挡板 |

## 项目目录约定

每个项目目录包含：

| 内容 | 说明 |
|---|---|
| `README.md` | 玩法、操作、部署步骤、可调参数、实现要点 |
| 源码 | 可直接上传到板子的 `.py` |

## 通用部署流程

```powershell
# 0) 先关掉 MobaXterm 等串口终端（串口独占）
# 1) 上传（板载文件名按项目需要命名，如 game.py）
python tools/repl_probe.py COM11 put projects/breakout/breakout.py game.py
# 2) 复位，让新代码生效（必须，否则 sys.modules 里还是旧的）
python tools/repl_probe.py COM11 reset
```

在 REPL 里手动启动：

```python
import controlBoardAlphaPiOne as c
c.init()
import game
game.Breakout().loop()
```

## 让项目开机自启

把板上的 `ht_main.py` 换成调用你的项目即可：

```python
import game


def Start(static_buf):
    game.run(static_buf)
```

原版 `ht_main.py` 已备份在 `firmware/com11_20220912/rootfs/`，随时可还原：

```powershell
python tools/repl_probe.py COM11 put firmware/com11_20220912/rootfs/ht_main.py
python tools/repl_probe.py COM11 reset
```

## 开发前建议

1. 先看 `docs/AlphaPi_游戏机（COM11）分析报告.md` §10「实战：打砖块游戏」，
   里面记录了屏幕 API 的**元组坐标约定**和**文字 16×16 白色**这两个硬限制
2. 涉及硬件输入时，参考 `firmware/com11_20220912/disasm/remoteControlSensorOne.mpy.txt`
   里的 `status_list` 索引语义
3. 改完记得 `reset`，否则会以为"改了没反应"
