# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

static_buf=bytearray(40960)

import network
import webrepl
import time

WIFI_SSID = "TP-LINK_F18C"
WIFI_PASS = "18143463550"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("连接WiFi")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(15):
            if wlan.isconnected():
                break
            time.sleep(1)
    if wlan.isconnected():
        print("IP:", wlan.ifconfig()[0])
    else:
        print("WiFi失败")

connect_wifi()
try:
    webrepl.start()
    print("WebREPL 8266启动")
except Exception as e:
    print("WebREPL启动异常", e)



