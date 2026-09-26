import hashlib, os

ROOT = r"./firmware/com10_20221028/rootfs"
OUT = r"./firmware/com10_20221028/MANIFEST.md"

files = []
for dp, _, fs in os.walk(ROOT):
    for f in fs:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        data = open(p, "rb").read()
        h = hashlib.sha256(data).hexdigest()
        files.append((rel, len(data), h))

files.sort(key=lambda x: x[0].lower())

lines = [
    "# 校验清单 MANIFEST（rootfs 全量备份 · %d 文件）" % len(files),
    "",
    "> 由 `python tools/_mkmanifest.py` 生成；SHA256 基于文件原始字节。",
    "> 用途：日后核对 `firmware/com10_20221028/rootfs/` 是否与 2026-09-24 这次全量备份一致。",
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
    "root=r'firmware/com10_20221028/rootfs'; \\",
    "[print(hashlib.sha256(open(os.path.join(d,f),'rb').read()).hexdigest(), os.path.relpath(os.path.join(d,f),root)) \\",
    " for d,_,fs in os.walk(root) for f in fs]\"",
    "```",
    "",
]

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote", len(files), "entries ->", OUT)
