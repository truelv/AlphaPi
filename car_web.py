#!/usr/bin/env python3
# car_web.py —— AlphaPi-One 小车 网页遥控服务（纯 Python 标准库，无依赖）
#
# 运行：
#     python car_web.py                 # 默认监听 0.0.0.0:8080
#     python car_web.py --port 8080 --board 192.168.1.16
# 然后手机/电脑浏览器打开  http://<本机IP>:8080  即可用虚拟摇杆+按钮控车。
#
# 说明：
#   - 板子需与运行本服务的主机在同一局域网（板子 STA 模式，IP 形如 192.168.1.16）。
#   - 默认向 UDP 广播 255.255.255.255:1000 发送，无需知道板子 IP（也可 --board 指定）。
#   - 协议：{"token":"","message":"...","value":"..."}

import argparse
import json
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BOARD_IP = "255.255.255.255"
BOARD_PORT = 1000
TOKEN = ""

PAGE = """<!doctype html>
<html lang="zh"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>AlphaPi 遥控</title>
<style>
*{box-sizing:border-box;-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent}
html,body{margin:0;height:100%;background:#0f172a;color:#e2e8f0;
  font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
.app{max-width:520px;margin:0 auto;padding:12px;display:flex;flex-direction:column;gap:12px;height:100%}
h1{font-size:16px;margin:4px 0;color:#38bdf8;text-align:center}
.row{display:flex;gap:10px;align-items:center;justify-content:center}
.pad{position:relative;width:min(78vw,340px);aspect-ratio:1;margin:0 auto;
  background:radial-gradient(circle at 50% 45%,#1e293b,#0b1220);border:2px solid #334155;border-radius:50%;
  touch-action:none}
.knob{position:absolute;left:50%;top:50%;width:34%;aspect-ratio:1;transform:translate(-50%,-50%);
  background:radial-gradient(circle at 40% 35%,#7dd3fc,#0ea5e9);border-radius:50%;
  box-shadow:0 6px 18px rgba(56,189,248,.5)}
.axis{position:absolute;background:#1e293b}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
button{font-size:17px;padding:16px 8px;border-radius:12px;border:1px solid #334155;
  background:#1e293b;color:#e2e8f0;font-weight:600}
button:active{background:#334155;transform:scale(.97)}
.big{grid-column:span 3;background:#7f1d1d;border-color:#b91c1c;color:#fff;font-size:20px;padding:20px}
.speed{display:flex;align-items:center;gap:10px;font-size:14px;color:#94a3b8}
input[type=range]{flex:1}
.tag{text-align:center;color:#64748b;font-size:12px}
</style></head>
<body><div class="app">
<h1>AlphaPi 小车遥控</h1>
<div class="pad" id="pad"><div class="knob" id="knob"></div></div>
<div class="speed">速度 <input type="range" id="spd" min="20" max="100" value="60">
  <span id="spdv">60</span></div>
<div class="grid">
  <button id="bstop">停</button>
  <button id="bclaw_o">开爪</button>
  <button id="bclaw_c">合爪</button>
  <button id="blight_on">开灯</button>
  <button id="blight_off">关灯</button>
  <button id="bup">前进</button>
</div>
<button class="big" id="bemerg">急停</button>
<div class="tag" id="tag">拖动摇杆控制 · 松手停车</div>
</div>
<script>
const pad=document.getElementById('pad'),knob=document.getElementById('knob');
const spd=document.getElementById('spd'),spdv=document.getElementById('spdv');
const tag=document.getElementById('tag');
let dragging=false, timer=null, lr=null;
spd.oninput=()=>{spdv.textContent=spd.value};

function api(message,value){
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({message:message,value:value===undefined?'':String(value)})}).catch(()=>{});
  tag.textContent=message+(value!==undefined&&value!==''?' '+value:'');
}
function stick(px,py){ // px,py: -1..1 (y 向上为正)
  const s=parseInt(spd.value)/100;
  let l=py+px, r=py-px;                 // 差速：右转 px>0 -> 左轮快
  l=Math.max(-1,Math.min(1,l)); r=Math.max(-1,Math.min(1,r));
  return [Math.round(l*s*100),Math.round(r*s*100)];
}
function setKnob(dx,dy){ knob.style.transform=`translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`; }

function pos2vec(e){
  const R=pad.getBoundingClientRect(), cx=R.left+R.width/2, cy=R.top+R.height/2;
  let dx=e.clientX-cx, dy=e.clientY-cy;
  const max=R.width/2*0.82, d=Math.hypot(dx,dy);
  if(d>max){dx*=max/d;dy*=max/d;}
  setKnob(dx,dy);
  return [dx/max, -dy/max];             // 归一化，y 取反（向上为正）
}
function start(e){dragging=true;pad.setPointerCapture(e.pointerId);move(e);
  timer=setInterval(()=>{if(lr)api('drive',lr[0]+','+lr[1]);},120);}
function move(e){if(!dragging)return;const[px,py]=pos2vec(e);lr=stick(px,py);api('drive',lr[0]+','+lr[1]);}
function end(e){dragging=false;lr=null;setKnob(0,0);if(timer){clearInterval(timer);timer=null;}api('停');}
pad.addEventListener('pointerdown',start);
pad.addEventListener('pointermove',move);
pad.addEventListener('pointerup',end);
pad.addEventListener('pointercancel',end);

document.getElementById('bup').onclick=()=>api('上',parseInt(spd.value));
document.getElementById('bstop').onclick=()=>api('停');
document.getElementById('bemerg').onclick=()=>api('停');
document.getElementById('bclaw_o').onclick=()=>api('开爪');
document.getElementById('bclaw_c').onclick=()=>api('合爪');
document.getElementById('blight_on').onclick=()=>api('开灯');
document.getElementById('blight_off').onclick=()=>api('关灯');
</script></body></html>"""


def send_udp(message, value=""):
    payload = json.dumps({"token": TOKEN, "message": message, "value": str(value)}).encode("utf-8")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except Exception:
        pass
    s.sendto(payload, (BOARD_IP, BOARD_PORT))
    s.close()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/" or u.path == "/index.html":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif u.path == "/api":
            q = parse_qs(u.query)
            m = q.get("m", [""])[0]
            v = q.get("v", [""])[0]
            if m:
                send_udp(m, v)
            self._json({"ok": bool(m), "message": m, "value": v})
        else:
            self._json({"ok": False, "err": "not found"}, 404)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/api":
            self._json({"ok": False, "err": "not found"}, 404)
            return
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n) if n else b"{}"
        try:
            d = json.loads(raw.decode("utf-8"))
        except Exception:
            d = {}
        m = str(d.get("message", ""))
        v = d.get("value", "")
        if m:
            send_udp(m, v)
        self._json({"ok": bool(m), "message": m, "value": v})


def serve(host="0.0.0.0", port=8080, board_ip=None):
    global BOARD_IP
    if board_ip:
        BOARD_IP = board_ip
    httpd = ThreadingHTTPServer((host, port), Handler)
    print("web remote: http://%s:%d  -> board udp %s:%d" % (
        socket.gethostbyname(socket.gethostname()) if host == "0.0.0.0" else host,
        port, BOARD_IP, BOARD_PORT))
    httpd.serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--board", default=None, help="板子 IP，默认广播 255.255.255.255")
    a = ap.parse_args()
    try:
        serve(port=a.port, board_ip=a.board)
    except KeyboardInterrupt:
        pass
