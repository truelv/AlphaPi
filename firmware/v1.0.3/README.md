# 固件 v1.0.3（厂商迭代版）

> 原仓库 `v1.0.3/` 目录。厂商在第 1 代（2020）之后、第 2 代之前发布的一版固件，
> 主控模块改名为 `controlBoard`。
> ⚠️ **它不是第 2 代板子上的固件**，仅作版本演进参考。

## 版本特征

| 项目 | 本版（v1.0.3） | 对比第 1 代（v2020_07_31） |
|---|---|---|
| 主控模块 | `controlBoard.mpy`（9.58KB） | `control_board_v1.mpy`（8.07KB，已改名并增大 1.5KB） |
| `basic.mpy` | 3.06KB | 3.08KB |
| 文件系统恢复阈值 | 文件数 < 15 | 文件数 < 10 |
| 分块写盘 | 一次性写入 | 64KB 分块 |
| 音频 `.dat` | 13 个（同名同大小） | 13 个 |
| 灯带 / 红外模块 | 已合入或未单独提供 | 独立 `.mpy` |

---

## 目录内容

### `main.py`（顶层）

简化后的启动脚本，单文件形式（与 `rootfs/main.py` 是两种写法）。

### `rootfs/` — 板载文件系统

| 文件 | 说明 |
|---|---|
| `boot.py` | 启动脚本 |
| `main.py` | 文件系统恢复 + 启动 |
| `basic.mpy` | `DataStruct` 运行时 |
| `controlBoard.mpy` | **主控模块（已改名）** |
| `alert.dat` 等 13 个 `.dat` | 音频资源 |

`main.py` 的关键差异——改成一次性读入：

```python
addr = 0x160000

def readFile(length):
    global addr
    temp_buf = bytearray(length)
    esp.flash_read(addr, temp_buf)
    addr += length
    return temp_buf
```

---

## ⚠️ 缺少反汇编

本目录**没有提供反汇编产物**，新版 API 未知。要分析需自行执行：

```powershell
python tools/mpy-tool.py -d firmware/v1.0.3/rootfs/controlBoard.mpy > firmware/v1.0.3/disasm/controlBoard.mpy.txt
```

（待办的比对工作：与 `control_board_v1` 做 diff，找出这 1.5KB 增量新增了什么。）
