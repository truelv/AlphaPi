import serial, time, sys

PORT = "COM10"
BAUD = 115200
SYNC = b"\xc0\x00\x08\x24\x00\x00\x00\x00\x00\x07\x07\x12\x20" + b"\x00"*32 + b"\xc0"

def open_ser():
    return serial.Serial(PORT, BAUD, timeout=0.5)

def read_until(ser, tok, t=4.0):
    buf=b""; end=time.time()+t
    while time.time()<end:
        d=ser.read(512)
        if d:
            buf+=d
            if tok in buf: return buf
    return buf

def try_boot(pulse, hold, holdval):
    ser=open_ser()
    # hold the other line
    if hold=="RTS": ser.setRTS(holdval); 
    if hold=="DTR": ser.setDTR(holdval)
    # pulse the reset line low then high
    if pulse=="DTR":
        ser.setDTR(False); 
    else:
        ser.setRTS(False)
    time.sleep(0.15)
    if pulse=="DTR": ser.setDTR(True)
    else: ser.setRTS(True)
    time.sleep(2.5)
    # is it still in download mode? send sync
    ser.reset_input_buffer()
    ser.write(SYNC); time.sleep(0.8)
    r=ser.read(64)
    in_dl = (b"\xc0\x01\x08" in r)
    print("pulse=%s hold=%s(%s) -> in_download_mode=%s" % (pulse, hold, holdval, in_dl))
    if in_dl:
        ser.close(); return None
    # try raw REPL
    ser.write(b"\x03\x03"); time.sleep(0.3); ser.reset_input_buffer()
    ser.write(b"\x01"); time.sleep(0.5)
    rr=read_until(ser, b"raw REPL", t=3.0)
    if b"raw REPL" not in rr:
        print("  raw repl fail:", repr(rr[:80])); ser.close(); return None
    print("  RAW REPL OK")
    return ser

for combo in [("DTR","RTS",True),("DTR","RTS",False),("RTS","DTR",True),("RTS","DTR",False)]:
    ser=try_boot(*combo)
    if ser:
        # run scan, write to /scan_out.txt
        scan=r'''
import machine
out=[]
KNOWN={0,3,8,9,38,39,40,41,42,45}
out.append("=== GPIO scan ===")
for p in range(0,49):
    if p in KNOWN:
        out.append("GPIO%02d (known bus)"%p); continue
    try:
        pin=machine.Pin(p,machine.Pin.IN,machine.Pin.PULL_UP); u=pin.value()
        pin.init(machine.Pin.IN,machine.Pin.PULL_DOWN); d=pin.value()
        tag="" if (u==1 and d==0) else "  <== CONNECTED"
        out.append("GPIO%02d PU=%d PD=%d%s"%(p,u,d,tag))
    except Exception as e:
        out.append("GPIO%02d ERR"%p)
out.append("=== I2C scan ===")
def si(scl,sda):
    try:
        i=machine.SoftI2C(scl=machine.Pin(scl),sda=machine.Pin(sda),freq=100000)
        return str(i.scan())
    except Exception as e:
        return "ERR"
out.append("car(9,8):"+si(9,8))
out.append("accel(7,6):"+si(7,6))
out.append("lcd(5,4):"+si(5,4))
out.append("=== ADC ===")
for p in [1,2,4,5,6,7,10,11,12,13,14,15,16,17,18,34,35,36,37,39]:
    try:
        a=machine.ADC(machine.Pin(p)); a.atten(machine.ADC.ATTN_11DB)
        out.append("ADC GPIO%02d=%d"%(p,a.read_u16()))
    except Exception as e:
        out.append("ADC GPIO%02d ERR"%p)
f=open('/scan_out.txt','w'); f.write("\n".join(out)); f.close()
print("SCAN_DONE")
'''
        payload=scan.encode()+b"\x04"
        for i in range(0,len(payload),128):
            ser.write(payload[i:i+128]); time.sleep(0.03)
        raw=read_until(ser,b"\x04>",t=20.0)
        print("EXEC:", repr(raw[:300]))
        ser.close()
        sys.exit(0)
print("ALL COMBOS FAILED -> need physical power cycle")
