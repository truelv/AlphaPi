#!/usr/bin/env python3
# car_web.py —— AlphaPi-One 小车 网页遥控服务（纯 Python 标准库，无依赖）
#
# 运行：
#     python car_web.py                 # 默认监听 0.0.0.0:8080
#     python car_web.py --port 8080 --board 192.168.1.16
# 手机/电脑浏览器打开  http://<本机IP>:8080  即可控车。
#
# 操作：
#   - 方向键（按住走、松手停）：前进 / 后退 / 左转 / 右转 / 停
#   - 虚拟摇杆：比例差速（前后 + 转向）
#   - 功能键：开爪 / 合爪 / 开灯 / 关灯
#   - 大号急停
#
# 说明：
#   - 板子需与运行本服务的主机在同一局域网（板子 STA 模式，IP 形如 192.168.1.16）。
#   - 默认向 UDP 广播 255.255.255.255:1000 发送，无需知道板子 IP（也可 --board 指定）。
#   - 协议：{"token":"","message":"...","value":"..."}

import argparse
import json
import socket
import sys
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BOARD_IP = "255.255.255.255"
BOARD_PORT = 1000
TOKEN = ""
LISTEN_PORT = 1000            # 监听小车广播的心跳/回执（与板子发送端口一致）

_STATUS = {"t": 0.0, "msg": "", "val": "", "ip": "", "cmd": ""}
_STATUS_LOCK = threading.Lock()


def start_listener(port=LISTEN_PORT):
    """后台线程：监听小车广播的心跳(hb)/回执(ack)，用于网页显示在线状态。"""
    def loop():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception:
            pass
        try:
            s.bind(("0.0.0.0", port))
        except Exception as e:
            print("status listener disabled (%s)" % e)
            return
        while True:
            try:
                data, _ = s.recvfrom(1024)
            except Exception:
                continue
            try:
                d = json.loads(data.decode("utf-8", "replace"))
            except Exception:
                continue
            m = str(d.get("message", ""))
            v = str(d.get("value", ""))
            with _STATUS_LOCK:
                _STATUS["t"] = time.time()
                _STATUS["msg"] = m
                _STATUS["val"] = v
                if m == "hb" and v:
                    _STATUS["ip"] = v
                elif m == "ack" and v:
                    _STATUS["cmd"] = v
    threading.Thread(target=loop, daemon=True).start()

PAGE = """<!doctype html>
<html lang="zh"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>AlphaPi 遥控</title>
<style>
*{box-sizing:border-box;-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent}
html,body{margin:0;min-height:100%;background:#0f172a;color:#e2e8f0;
  font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
.app{max-width:600px;margin:0 auto;padding:12px;display:flex;flex-direction:column;gap:12px}
h1{font-size:16px;margin:4px 0;color:#38bdf8;text-align:center}
.speed{display:flex;align-items:center;gap:10px;font-size:14px;color:#94a3b8}
input[type=range]{flex:1}
.ctrls{display:flex;flex-wrap:wrap;gap:18px;justify-content:center;align-items:center}

/* 摇杆 */
.pad{position:relative;width:min(46vw,250px);aspect-ratio:1;
  background:radial-gradient(circle at 50% 45%,#1e293b,#0b1220);border:2px solid #334155;border-radius:50%;
  touch-action:none}
.knob{position:absolute;left:50%;top:50%;width:34%;aspect-ratio:1;transform:translate(-50%,-50%);
  background:radial-gradient(circle at 40% 35%,#7dd3fc,#0ea5e9);border-radius:50%;
  box-shadow:0 6px 18px rgba(56,189,248,.5)}

/* 方向键 */
.dpad{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);
  gap:8px;width:min(46vw,250px);aspect-ratio:1;touch-action:none}
.dp{border:1px solid #334155;background:#1e293b;color:#e2e8f0;border-radius:12px;
  font-size:22px;font-weight:700;display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:0;line-height:1.1;touch-action:none}
.dp small{font-size:11px;color:#94a3b8;font-weight:400}
.dp:active{background:#334155;transform:scale(.96)}
.dp.up{grid-area:1/2}.dp.left{grid-area:2/1}.dp.stop{grid-area:2/2;background:#7f1d1d;border-color:#b91c1c}
.dp.right{grid-area:2/3}.dp.down{grid-area:3/2}

.funcs{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.funcs button{font-size:15px;padding:14px 6px;border-radius:12px;border:1px solid #334155;
  background:#1e293b;color:#e2e8f0;font-weight:600}
.funcs button:active{background:#334155}
.big{width:100%;padding:20px;border-radius:14px;border:1px solid #b91c1c;background:#7f1d1d;
  color:#fff;font-size:20px;font-weight:700}
.big:active{background:#991b1b}
.tag{text-align:center;color:#64748b;font-size:12px;min-height:16px}
.st{text-align:center;font-size:13px;color:#64748b;margin:-4px 0 0}
.st.ok{color:#22c55e}
.st.weak{color:#eab308}
.st.off{color:#ef4444}
</style></head>
<body><div class="app">
<h1>AlphaPi 小车遥控</h1>
<div class="st" id="st">● 检测中…</div>

<div class="speed">速度 <input type="range" id="spd" min="20" max="100" value="60">
  <span id="spdv">60</span></div>

<div class="ctrls">
  <div class="pad" id="pad"><div class="knob" id="knob"></div></div>
  <div class="dpad" id="dpad">
    <button class="dp up"    data-dir="上">▲<small>前进</small></button>
    <button class="dp left"  data-dir="左">◀<small>左转</small></button>
    <button class="dp stop"  data-dir="停">■<small>停</small></button>
    <button class="dp right" data-dir="右">▶<small>右转</small></button>
    <button class="dp down"  data-dir="下">▼<small>后退</small></button>
  </div>
</div>

<div class="funcs">
  <button id="bclaw_o">开爪</button>
  <button id="bclaw_c">合爪</button>
  <button id="blight_on">开灯</button>
  <button id="blight_off">关灯</button>
</div>
<button class="big" id="bemerg">急停</button>
<div class="tag" id="tag">方向键按住走、松手停 · 摇杆比例控制</div>
</div>
<script>
const pad=document.getElementById('pad'),knob=document.getElementById('knob');
const spd=document.getElementById('spd'),spdv=document.getElementById('spdv');
const tag=document.getElementById('tag');
spd.oninput=()=>{spdv.textContent=spd.value};

function api(message,value){
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({message:message,value:value===undefined?'':String(value)})}).catch(()=>{});
  tag.textContent=message+(value!==undefined&&value!==''?' '+value:'');
}

/* ---------- 方向键：按住走，松手停 ---------- */
function bindHold(el,dir){
  let t=null;
  const send=()=>api(dir,parseInt(spd.value));
  const begin=(e)=>{e.preventDefault();send();if(!t)t=setInterval(send,200);};
  const stop=()=>{if(t){clearInterval(t);t=null;}api('停');};
  el.addEventListener('pointerdown',begin);
  el.addEventListener('pointerup',stop);
  el.addEventListener('pointercancel',stop);
  el.addEventListener('pointerleave',stop);
}
document.querySelectorAll('.dp').forEach(b=>bindHold(b,b.dataset.dir));

/* ---------- 摇杆：比例差速 ---------- */
let dragging=false,timer=null,lr=null;
function stick(px,py){                 // px,py: -1..1，py 向上为正
  const s=parseInt(spd.value)/100;
  let l=py-px, r=py+px;                // 右推(px>0) -> 右转；与官方语义一致
  l=Math.max(-1,Math.min(1,l)); r=Math.max(-1,Math.min(1,r));
  return [Math.round(l*s*100),Math.round(r*s*100)];
}
function setKnob(dx,dy){knob.style.transform=`translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;}
function pos2vec(e){
  const R=pad.getBoundingClientRect(),cx=R.left+R.width/2,cy=R.top+R.height/2;
  let dx=e.clientX-cx,dy=e.clientY-cy;const max=R.width/2*0.82,d=Math.hypot(dx,dy);
  if(d>max){dx*=max/d;dy*=max/d;}
  setKnob(dx,dy);return [dx/max,-dy/max];
}
function jstart(e){dragging=true;pad.setPointerCapture(e.pointerId);move(e);
  timer=setInterval(()=>{if(lr)api('drive',lr[0]+','+lr[1]);},150);}
function move(e){if(!dragging)return;const[px,py]=pos2vec(e);lr=stick(px,py);api('drive',lr[0]+','+lr[1]);}
function jend(){dragging=false;lr=null;setKnob(0,0);if(timer){clearInterval(timer);timer=null;}api('停');}
pad.addEventListener('pointerdown',jstart);
pad.addEventListener('pointermove',move);
pad.addEventListener('pointerup',jend);
pad.addEventListener('pointercancel',jend);

/* ---------- 功能键 ---------- */
document.getElementById('bclaw_o').onclick=()=>api('开爪');
document.getElementById('bclaw_c').onclick=()=>api('合爪');
document.getElementById('blight_on').onclick=()=>api('开灯');
document.getElementById('blight_off').onclick=()=>api('关灯');
document.getElementById('bemerg').onclick=()=>{if(timer){clearInterval(timer);timer=null;}api('停');};

/* ---------- 在线状态轮询 ---------- */
function cmdText(d){
  return (d.cmd?(' · 最后指令 '+d.cmd):'')+' · 速度 '+spd.value;
}
async function poll(){
  try{
    const d=await (await fetch('/status')).json();
    const el=document.getElementById('st');
    if(d.level==='ok'){el.className='st ok';el.textContent='● 在线'+(d.board?('  '+d.board):'')+'  '+d.ago+'s'+cmdText(d);}
    else if(d.level==='weak'){el.className='st weak';el.textContent='● 信号弱  '+d.ago+'s'+cmdText(d);}
    else{el.className='st off';el.textContent='● 离线';}
  }catch(e){}
}
setInterval(poll,1000);poll();
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
        elif u.path == "/status":
            with _STATUS_LOCK:
                t = _STATUS["t"]; ip = _STATUS["ip"]; cmd = _STATUS["cmd"]
            if t <= 0:
                level, ago = "off", -1
            else:
                ago = round(time.time() - t, 1)
                level = "ok" if ago < 2.5 else ("weak" if ago < 5.0 else "off")
            self._json({"online": level == "ok", "level": level, "ago": ago,
                        "board": ip, "cmd": cmd})
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
    start_listener()
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
