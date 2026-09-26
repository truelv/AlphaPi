import ujson

for s in ["abc", "\u505c", "\u4e0a"]:
    try:
        r = ujson.dumps({"m": s, "v": s})
        print("OK", r)
    except Exception as e:
        print("ERR", type(e).__name__, str(e))
print("DONE")
