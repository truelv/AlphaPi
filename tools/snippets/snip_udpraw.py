import socket, time, ujson, network
ap = network.WLAN(network.AP_IF)
if not ap.active():
    ap.active(True)
print("AP=" + str(ap.ifconfig()))
r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    r.bind(("0.0.0.0", 1000))
    print("BIND_OK")
except Exception as e:
    print("BIND_ERR=" + str(e))
r.settimeout(0)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg = ujson.dumps({"token": "", "message": "上", "value": "40"})
for a in ("192.168.4.1", "255.255.255.255", "127.0.0.1"):
    try:
        n = s.sendto(msg.encode(), (a, 1000))
        print("sent " + a + " n=" + str(n))
    except Exception as e:
        print("send " + a + " err=" + str(e))
    time.sleep_ms(250)
    try:
        d = r.recv(1024)
        print("recv " + a + " -> " + str(d))
    except Exception as e:
        print("recv " + a + " err=" + str(e))
print("OK")
