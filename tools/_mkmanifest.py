"""为某个 rootfs 全量备份生成 SHA256 校验清单 MANIFEST.md。

用法:
    python tools/_mkmanifest.py                      # 默认 com10_20221028（历史行为）
    python tools/_mkmanifest.py <rootfs目录> <输出md> ["备份说明"]

示例:
    python tools/_mkmanifest.py firmware/com13_20220808/rootfs \
        firmware/com13_20220808/MANIFEST.md "2026-09-26 这次全量备份"
"""
import hashlib
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else r"./firmware/com10_20221028/rootfs"
OUT = sys.argv[2] if len(sys.argv) > 2 else r"./firmware/com10_20221028/MANIFEST.md"
NOTE = sys.argv[3] if len(sys.argv) > 3 else "2026-09-24 这次全量备份"

# 相对仓库根目录的路径（用于打印复算命令）
ROOT_REL = os.path.relpath(ROOT).replace("\\", "/")

files = []
for dp, _, fs in os.walk(ROOT):
    for f in fs:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        data = open(p, "rb").read()
        h = hashlib.sha256(data).hexdigest()
        files.append((rel.replace("\\", "/"), len(data), h))

files.sort(key=lambda x: x[0].lower())

lines = [
    "# 校验清单 MANIFEST（rootfs 全量备份 · %d 文件）" % len(files),
    "",
    "> 由 `python tools/_mkmanifest.py` 生成；SHA256 基于文件原始字节。",
    "> 用途：日后核对 `%s/` 是否与 %s 一致。" % (ROOT_REL, NOTE),
    "",
    "| 文件 | 大小(B) | SHA256 |",
    "|---|---:|---|",
]
for rel, sz, h in files:
    lines.append("| `%s` | %d | `%s` |" % (rel, sz, h))

total = sum(s for _, s, _ in files)
lines += [
    "",
    "**合计：%d 个文件，%d 字节（%.1f KB）**" % (len(files), total, total / 1024),
    "",
    "## 校验方法",
    "",
    "重新计算并打印当前 rootfs 的 SHA256，与上面逐行比对即可：",
    "",
    "```powershell",
    "python -c \"import hashlib,os; \\",
    "root=r'%s'; \\" % ROOT_REL,
    "[print(hashlib.sha256(open(os.path.join(d,f),'rb').read()).hexdigest(), os.path.relpath(os.path.join(d,f),root)) \\",
    " for d,_,fs in os.walk(root) for f in fs]\"",
    "```",
    "",
]

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote %d entries -> %s" % (len(files), OUT))
