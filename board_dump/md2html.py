"""极简 Markdown -> HTML 转换器（无第三方依赖）。

支持：标题(#~######)、围栏代码块(```)、表格(| a | b |)、无序/有序列表、
引用(>)、水平线(---)、段落；行内：`code`、**bold**、[text](url)。
用法：python md2html.py <input.md> <output.html>
"""
import sys, html, re, os

CSS = """
:root{--bg:#0f172a;--card:#1e293b;--fg:#e2e8f0;--mut:#94a3b8;--acc:#38bdf8;--line:#334155;--code:#0b1220;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.7 -apple-system,"Segoe UI",Roboto,"Microsoft YaHei",sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:40px 24px 96px}
h1,h2,h3,h4{line-height:1.3;color:#f8fafc;margin:1.6em 0 .6em}
h1{font-size:2rem;border-bottom:2px solid var(--acc);padding-bottom:.3em}
h2{font-size:1.45rem;border-bottom:1px solid var(--line);padding-bottom:.25em}
h3{font-size:1.15rem;color:var(--acc)}
a{color:var(--acc)}
code{background:var(--code);border:1px solid var(--line);border-radius:4px;
  padding:.1em .35em;font-family:"JetBrains Mono",Consolas,monospace;font-size:.88em;color:#7dd3fc}
pre{background:var(--code);border:1px solid var(--line);border-radius:8px;
  padding:14px 16px;overflow:auto}
pre code{background:none;border:none;padding:0;color:#cbd5e1}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:.94em}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--card);color:#f1f5f9}
tr:nth-child(even) td{background:rgba(148,163,184,.06)}
blockquote{margin:1em 0;padding:.4em 1em;border-left:3px solid var(--acc);
  background:rgba(56,189,248,.08);color:#cbd5e1}
hr{border:none;border-top:1px solid var(--line);margin:2.2em 0}
ul,ol{padding-left:1.5em}
li{margin:.2em 0}
strong{color:#fff}
.meta{color:var(--mut);font-size:.85em;margin-bottom:2em}
@media print{
  :root{--bg:#ffffff;--card:#f1f5f9;--fg:#111827;--mut:#4b5563;--acc:#0369a1;--line:#cbd5e1;--code:#f8fafc;}
  *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  body{background:#fff}
  .wrap{max-width:none;padding:0}
  h1,h2,h3,h4{color:#0f172a}
  pre{border:1px solid #cbd5e1}
  pre code{color:#0f172a}
  table{font-size:.85em}
  tr,td,th{page-break-inside:avoid}
  h2,h3{page-break-after:avoid}
}
"""


def inline(t):
    t = html.escape(t, quote=False)
    # 行内代码优先（占位保护，避免其中 ** 被转义）
    codes = []

    def _code(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    t = re.sub(r"`([^`]+)`", _code, t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    for i, c in enumerate(codes):
        t = t.replace("\x00%d\x00" % i, "<code>%s</code>" % c)
    return t


def convert(md):
    lines = md.split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        # 围栏代码块
        if ln.strip().startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(buf)))
            continue
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2).strip()), lvl))
            i += 1; continue
        # 水平线
        if re.match(r"^\s*-{3,}\s*$", ln):
            out.append("<hr>"); i += 1; continue
        # 表格
        if ln.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            def cells(row):
                return [c.strip() for c in row.strip().strip("|").split("|")]
            head = cells(ln)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(cells(lines[i])); i += 1
            h = "".join("<th>%s</th>" % inline(c) for c in head)
            body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r) for r in rows)
            out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (h, body))
            continue
        # 引用
        if ln.strip().startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            out.append("<blockquote>%s</blockquote>" % "<br>".join(inline(x) for x in buf))
            continue
        # 列表
        if re.match(r"^\s*[-*]\s+", ln):
            buf = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                buf.append("<li>%s</li>" % inline(re.sub(r"^\s*[-*]\s+", "", lines[i]))); i += 1
            out.append("<ul>%s</ul>" % "".join(buf)); continue
        if re.match(r"^\s*\d+\.\s+", ln):
            buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append("<li>%s</li>" % inline(re.sub(r"^\s*\d+\.\s+", "", lines[i]))); i += 1
            out.append("<ol>%s</ol>" % "".join(buf)); continue
        # 空行
        if not ln.strip():
            i += 1; continue
        # 段落
        buf = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6}\s|>|\s*[-*]\s|\s*\d+\.\s|\s*```|\s*\|)", lines[i]):
            buf.append(lines[i]); i += 1
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf)))
    return "\n".join(out)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, "r", encoding="utf-8") as f:
        md = f.read()
    title = os.path.splitext(os.path.basename(src))[0]
    doc = ("<!doctype html><html lang=\"zh\"><head><meta charset=\"utf-8\">"
           "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
           "<title>%s</title><style>%s</style></head><body><div class=\"wrap\">%s</div></body></html>"
           % (html.escape(title), CSS, convert(md)))
    with open(dst, "w", encoding="utf-8") as f:
        f.write(doc)
    print("HTML written: %s (%d bytes)" % (dst, len(doc)))


if __name__ == "__main__":
    main()
