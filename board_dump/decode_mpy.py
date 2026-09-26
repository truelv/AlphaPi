import base64, os, re

src = "board_dump/full_out.txt"
out_dir = "board_dump/dumped"
os.makedirs(out_dir, exist_ok=True)

with open(src, "r", encoding="utf-8") as f:
    txt = f.read()

starts = [m.start() for m in re.finditer("FULL_START", txt)]
end_idx = txt.rfind("FULL_END")
body = txt[starts[-1] + len("FULL_START"):end_idx] if (starts and end_idx >= 0) else ""

for part in body.split("####"):
    part = part.strip("\r\n ")
    if not part:
        continue
    lines = part.split("\n")
    fn = lines[0].strip()
    if fn.endswith(":ERR:"):
        print("ERR block:", fn)
        continue
    # 逐行（每块 512 字节）独立 base64 解码后拼接
    # —— 不能整体解，因为每个块各自补了 '=' 填充，拼接后中间的 '=' 会让解码器提前停止
    data = b""
    try:
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            data += base64.b64decode(line)
        with open(os.path.join(out_dir, fn), "wb") as f:
            f.write(data)
        print("SAVED %s (%d bytes)" % (fn, len(data)))
    except Exception as e:
        print("decode fail %s: %s" % (fn, e))
