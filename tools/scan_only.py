import serial, time, sys, os

PORT = "COM10"
BAUD = 115200

def try_enter_raw(ser):
    ser.write(b"\x03"); time.sleep(0.4)          # Ctrl-C
    ser.write(b"\x03"); time.sleep(0.4)          # Ctrl-C
    ser.reset_input_buffer()
    ser.write(b"\x01")                            # Ctrl-A -> raw REPL
    buf = b""
    end = time.time() + 3.0
    while time.time() < end:
        d = ser.read(200)
        if d:
            buf += d
            if b"raw REPL" in buf:
                return True
    return False

# scan payload：用 START/END 标记框住真正要抓的输出
# i2c_pair: (sda, scl) 或 None；只扫这一对，避免某对卡死拖垮整段
def build_scan(i2c_pair):
    s = []
    s.append('print("SCAN_START")')
    s.append('import machine,os')
    s.append('out=[]')
    s.append('out.append("FREQ="+str(machine.freq()))')
    s.append('out.append("UID="+str(machine.unique_id()))')
    s.append('for n in range(0,40):')
    s.append(' try:')
    s.append('  p=machine.Pin(n); v=p.value(); out.append("GPIO%d=%s"%(n,repr(v)))')
    s.append(' except Exception as e:')
    s.append('  out.append("GPIO%d=-"%(n))')
    s.append('try:')
    s.append(' out.append("FILES="+";".join(os.listdir()))')
    s.append('except Exception as e:')
    s.append(' out.append("ls_err:"+str(e))')
    s.append('for m in ("network","esp","esp32","urequests","umqtt","bluetooth","btree","framebuf","sdcard","uctypes","neopixel","dht"):')
    s.append(' try:')
    s.append('  __import__(m); out.append("MOD:"+m)')
    s.append(' except Exception:')
    s.append('  pass')
    s.append('for n in range(0,40):')
    s.append(' try:')
    s.append('  a=machine.ADC(machine.Pin(n)); out.append("ADC%d=%s"%(n,repr(a.read())))')
    s.append(' except Exception as e:')
    s.append('  out.append("ADC%d=-"%(n))')
    s.append('for host,mosi,miso,sck in [(1,13,12,14),(2,23,19,18),(1,11,13,12)]:')
    s.append(' try:')
    s.append('  machine.SPI(host,baudrate=1000000,mosi=machine.Pin(mosi),miso=machine.Pin(miso),sck=machine.Pin(sck))')
    s.append('  out.append("SPI%d ok m%d mi%d sck%d"%(host,mosi,miso,sck))')
    s.append(' except Exception as e:')
    s.append('  out.append("SPI%d err:%s"%(host,str(e)))')
    if i2c_pair:
        sda, scl = i2c_pair
        s.append('try:')
        s.append(' i2c=machine.I2C(0,sda=machine.Pin(%d),scl=machine.Pin(%d),freq=100000,timeout=20000)' % (sda, scl))
        s.append(' d=i2c.scan()')
        s.append(' out.append("I2C sda%d scl%d=%%s" %% ([hex(x) for x in d]))' % (sda, scl))
        s.append('except Exception as e:')
        s.append(' out.append("I2C sda%d scl%d err=%%s" %% (str(e)))' % (sda, scl))
    s.append('print("\\n".join(out))')
    s.append('print("SCAN_END")')
    return "\n".join(s) + "\n"

def exec_and_capture(ser):
    # 分块慢发，边发边丢弃回显，避免 TX 缓冲溢出
    pair = None
    raw = os.environ.get("I2C_PAIR", "")
    if raw:
        try:
            a, b = raw.split(",")
            pair = (int(a.strip()), int(b.strip()))
        except Exception:
            pair = None
    code = build_scan(pair).encode()
    i = 0
    while i < len(code):
        chunk = code[i:i+32]
        ser.write(chunk)
        time.sleep(0.01)
        # 丢弃回显
        deadline = time.time() + 0.5
        while time.time() < deadline:
            d = ser.read(256)
            if d:
                deadline = time.time() + 0.5
        i += 32
    time.sleep(0.3)  # 等回显收尾
    ser.reset_input_buffer()
    ser.write(b"\x04")  # Ctrl-D 执行
    # 读取输出，抓 START..END（回显里也有一份标记，取最后一次出现的）
    buf = b""
    end = time.time() + 6.0
    while time.time() < end:
        d = ser.read(512)
        if d:
            buf += d
            if b"SCAN_END" in buf:
                break
    txt = buf.decode("utf-8", "replace")
    # 写调试原始缓冲
    try:
        with open("board_dump/raw_cap.txt", "w", encoding="utf-8") as dbg:
            dbg.write("LEN=%d\n" % len(buf))
            dbg.write(repr(buf))
    except Exception:
        pass
    # 取最后一次 SCAN_START 与 SCAN_END 之间
    starts = [m.start() for m in __import__("re").finditer("SCAN_START", txt)]
    end_idx = txt.rfind("SCAN_END")
    result = ""
    if starts and end_idx >= 0:
        s = starts[-1] + len("SCAN_START")
        result = txt[s:end_idx].strip("\r\n ")
    return result

def main():
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2.0)
    ok = False
    for attempt in range(6):
        if try_enter_raw(ser):
            ok = True
            break
        time.sleep(0.5)
    if not ok:
        print("NO_RAW")
        ser.close()
        sys.exit(0)
    print("RAW_OK")
    result = exec_and_capture(ser)
    with open("board_dump/scan_out.txt", "w", encoding="utf-8") as f:
        f.write(result)
    print("SCAN_SAVED bytes=%d" % len(result))
    print(result)
    ser.close()

if __name__ == "__main__":
    main()
