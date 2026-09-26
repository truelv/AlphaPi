"""检查 Markdown 文档里的相对链接/图片是否都指向真实存在的文件。

用法:
    python tools/check_links.py              # 检查仓库内所有 .md
    python tools/check_links.py docs         # 只检查指定目录/文件（可多个）
    python tools/check_links.py docs README.md

忽略: http(s)://、mailto:、纯锚点 (#...)
支持: ](path)、](<path with spaces>)、](path#anchor)、![img](path)

例外: 单独一行写 <!-- check-links: off --> 则整份跳过。
      用于"部署后才成立"的文档——例如树莓派侧的 README，其相对路径以
      `/home/pi/Codes/` 为基准，在仓库里检查必然"断链"。
      （必须单独成行，这样文档里"顺口提到"这个标记不会把自己也跳过。）

退出码: 有断链时返回 1（方便接进 CI / 提交前跑一下）
"""

import os
import re
import sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".codebuddy"}
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "data:", "#")
# 必须"单独成行"的 HTML 注释；避免文档里仅提及该标记就被跳过
IGNORE_RE = re.compile(r"^[ \t]*<!--\s*check-links:\s*off\s*-->[ \t]*$", re.MULTILINE)

LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def md_files(targets):
    for t in targets:
        p = t if os.path.isabs(t) else os.path.join(ROOT, t)
        if os.path.isfile(p):
            yield p
            continue
        for cur, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                if f.lower().endswith(".md"):
                    yield os.path.join(cur, f)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def is_ignored(path):
    try:
        return bool(IGNORE_RE.search(read(path)))
    except OSError:
        return False


def check(path):
    """返回 [(行号, 原始链接, 解析后的绝对路径)]"""
    broken = []
    try:
        text = read(path)
    except OSError as exc:
        print("  ! 读不了 %s: %s" % (path, exc))
        return broken
    if IGNORE_RE.search(text):
        return broken
    for no, line in enumerate(text.splitlines(), 1):
        for raw in LINK.findall(line):
            link = raw.strip()
            if link.startswith("<") and link.endswith(">"):
                link = link[1:-1].strip()
            if not link or link.startswith(SKIP_PREFIX):
                continue
            link = link.split("#")[0].strip()
            if not link:
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), unquote(link)))
            if not os.path.exists(target):
                broken.append((no, raw.strip(), target))
    return broken


def main():
    targets = sys.argv[1:] or ["."]
    total = 0
    skipped = 0
    bad = 0
    for f in sorted(md_files(targets)):
        total += 1
        if is_ignored(f):
            skipped += 1
            continue
        broken = check(f)
        if broken:
            bad += 1
            print("%s" % os.path.relpath(f, ROOT))
            for no, raw, target in broken:
                print("  L%-4d %-46s -> %s" % (no, raw, os.path.relpath(target, ROOT)))
    print("\n检查 %d 个 Markdown 文件：%d 个存在断链，%d 个按标记跳过。"
          % (total, bad, skipped))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
