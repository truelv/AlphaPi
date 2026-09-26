import machine

# 已知总线脚：UART1(0=rx,3=tx) / 车用I2C(8=sda,9=scl) / SPI屏(38,39,40,41,42,45)
KNOWN = {0,3,8,9,38,39,40,41,42,45}

print("=== GPIO scan (PU/PD 不一致 = 有外设拉住) ===")
for p in range(0,49):
    if p in KNOWN:
        print("GPIO%-2d  (已知总线脚，跳过)" % p)
        continue
    try:
        pin = machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_UP)
        u = pin.value()
        pin.init(machine.Pin.IN, machine.Pin.PULL_DOWN)
        d = pin.value()
        flag = "" if (u==1 and d==0) else "  <== 有拉/被驱动"
        print("GPIO%-2d  PU=%d PD=%d%s" % (p, u, d, flag))
    except Exception as e:
        print("GPIO%-2d  ERR %s" % (p, e))

print("=== I2C scan ===")
def scan_i2c(scl, sda, freq=100000):
    try:
        i2c = machine.SoftI2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=freq)
        return i2c.scan()
    except Exception as e:
        return "ERR:%s" % e
print("车用I2C (scl=9,sda=8):", scan_i2c(9,8))
print("旧加速度计 (scl=7,sda=6):", scan_i2c(7,6))
print("手册12864 (scl=5,sda=4):", scan_i2c(5,4))

print("=== ADC 采样（电池/模拟量）===")
for p in [1,2,4,5,6,7,10,11,12,13,14,15,16,17,18,34,35,36,37,38,39]:
    try:
        adc = machine.ADC(machine.Pin(p))
        adc.atten(machine.ADC.ATTN_11DB)
        print("ADC GPIO%-2d = %d" % (p, adc.read_u16()))
    except Exception as e:
        print("ADC GPIO%-2d ERR %s" % (p, e))

print("=== done ===")
