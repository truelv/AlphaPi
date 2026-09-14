# 打砖块（Breakout）

跑在 **COM11 游戏机**上的打砖块小游戏，用摇杆控制挡板。

- 源码：`breakout.py`（单文件，约 200 行）
- 板上文件名：`game.py`
- 首次完成：2026-09-13

---

## 操作

| 操作 | 硬件 |
|---|---|
| 挡板左右移动 | **摇杆左右**（模拟量 0–1023，跟手） |
| 暂停 / 继续 | **按键 A**（`status_list[0]`） |
| 重新开始 | **按键 B**（`status_list[1]`） |

## 规则

- 4 行 × 5 列 = 20 块砖，每行一色：红 / 黄 / 绿 / 青
- 顶部左侧显示 `S<分数>`，右侧 `L<生命>`
- 打掉一块 +1 分；球碰挡板的**位置**决定反弹角度（打边缘角度大，打中间接近垂直）
- 漏球扣 1 条命，3 条命用完显示 `GAME OVER`
- 清空全部砖块显示 `WIN`
- 随时按 B 键重开

---

## 部署

```powershell
# 1) 先关掉 MobaXterm 串口会话（串口独占）
# 2) 上传
python tools/repl_probe.py COM11 put projects/breakout/breakout.py game.py
# 3) 复位使新代码生效
python tools/repl_probe.py COM11 reset
```

启动游戏（在 REPL 里，或 MobaXterm 中）：

```python
import controlBoardAlphaPiOne as c
c.init()
import game
game.Breakout().loop()      # 死循环，Ctrl-C 退出
```

---

## 代码结构

| 部分 | 说明 |
|---|---|
| 常量区 | 屏幕尺寸、挡板 / 球 / 砖块参数、`FRAME_MS` |
| `new_game()` | 重置一局并完成初始绘制 |
| `draw_*` / `erase_*` | 各元素的绘制与擦除（**只重绘变化区域**，不整屏刷新） |
| `new_ball()` | 重置球的位置与速度 |
| `finish(msg)` | 显示结束提示 |
| `step()` | 每帧推进：擦旧 → 移动 → 边界反弹 → 挡板碰撞 → 砖块碰撞 → 掉底判定 → 画新 |
| `loop()` | 主循环：读摇杆/按键 → 边沿检测 → 驱动 `step()` → 帧率控制 |
| `run()` | 初始化 + 启动（可作为 `ht_main.Start` 的入口） |

---

## 可调参数

| 参数 | 默认值 | 作用 |
|---|---|---|
| `PAD_W` | 34 | 挡板宽度，加大更容易接住 |
| `dx` / `dy` 初值（见 `new_ball()`） | 2 / -2 | 球速（每帧像素），改成 1 会明显变慢 |
| `BRICK_COLS` / `BRICK_ROWS` | 5 / 4 | 砖块布局 |
| `BRICK_W` / `BRICK_H` / `BRICK_DY` | 30 / 10 / 11 | 砖块尺寸与行距 |
| `FRAME_MS` | 16 | 帧间隔（约 60fps），加大则整体变慢 |

---

## 实现要点（都踩过坑）

1. **TFT 坐标是元组**：`tft.fillrect((x, y), (w, h), color)`，不是分开的 x/y 参数。
   写成 `fillrect(x, y, w, h, color)` 会抛 `TypeError: function takes 4 positional arguments`。
2. **文字固定 16×16、白色**：`controlBoardAlphaPiOne.showStringWithXY(x, y, s)` 内部写死
   `textzh((x, y), s, TFT.WHITE, sysfont_zh16)`，无法改颜色和字号。
   后果是**一行最多 10 个字符**（160 ÷ 16），提示语必须极短（`WIN` / `GAME OVER`）。
3. **按键必须做边沿检测**：`if st[0] and not self.btn_a`，否则长按会连续触发。
4. **`step()` 要自带结束保护**：开头 `if self.over: return`。
   否则结束后若仍被调用，球会反复掉底、生命值无限递减（实测掉到 −22）。
5. **只重绘变化区域**：球"先擦旧位置再画新位置"，挡板仅在坐标变化时擦画。
   整屏 160×128 刷新在 20MHz SPI 下约需 16ms，不适合每帧全刷。
6. **改完必须复位**：MicroPython 把已导入模块缓存在 `sys.modules`，不复位的话
   改了文件也看不到变化（`python tools/repl_probe.py COM11 reset`）。

---

## 想改成别的游戏

这份代码可以直接当模板：

- **换玩法**：复用 `10.2` 节的绘图 API（`fillrect` / `fillcircle` / `line` / `text`）
  和 `status_list` 输入映射，重写 `step()` 与 `loop()` 即可
- **贪吃蛇**：把屏幕按 16×16 或 8×8 网格化，用摇杆四方向控制，`fillrect` 画蛇身
- **加音效**：`controlBoardAlphaPiOne.playBeat*`（蜂鸣器）或 `play('alert.dat')`（音频）

改造时注意上面「实现要点」里的 6 条，尤其是 1、2、6。
