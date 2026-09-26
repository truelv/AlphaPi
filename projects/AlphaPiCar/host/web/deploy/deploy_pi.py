"""部署 AlphaPiCar 网页遥控到树莓派 (/home/pi/Codes/AlphaPiCar)。

用法:
    python projects/AlphaPiCar/host/web/deploy/deploy_pi.py
"""
import os
import paramiko

HOST = "192.168.1.27"
USER = "pi"
PWD = "wangchen"
BASE = "/home/pi/Codes"
PROJ = BASE + "/AlphaPiCar"

HERE = os.path.dirname(os.path.abspath(__file__))        # projects/AlphaPiCar/host/web/deploy
WEB = os.path.dirname(HERE)                              # projects/AlphaPiCar/host/web


def run(cli, cmd, sudo=False, timeout=60):
    if sudo:
        cmd = "echo '%s' | sudo -S bash -lc \"%s\"" % (PWD, cmd.replace('"', '\\"'))
    stdin, stdout, stderr = cli.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err


def sh(cli, cmd, sudo=False):
    code, out, err = run(cli, cmd, sudo=sudo)
    print("$ %s\n[%d] %s%s" % (cmd, code, out.strip(), ((" | ERR: " + err.strip()) if err.strip() else "")))
    return out


cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=PWD, timeout=10)
print("== connected to %s ==" % HOST)

sh(cli, "uname -a; python3 --version")
sh(cli, "mkdir -p %s/systemd" % PROJ)
sh(cli, "ls -la %s" % BASE)

sftp = cli.open_sftp()


def put(local_path, remote_path):
    with open(local_path, "rb") as f:
        data = f.read()
    with sftp.open(remote_path, "wb") as rf:
        rf.write(data)
    print("  -> %s (%d bytes)" % (remote_path, len(data)))


put(os.path.join(WEB, "car_web.py"), PROJ + "/car_web.py")
put(os.path.join(WEB, "car_remote_client.py"), PROJ + "/car_remote_client.py")
put(os.path.join(HERE, "pi_AlphaPiCar_README.md"), PROJ + "/README.md")
put(os.path.join(HERE, "alphaipi-web.service"), PROJ + "/systemd/alphaipi-web.service")
put(os.path.join(HERE, "pi_Codes_README.md"), BASE + "/README.md")
sftp.close()

sh(cli, "cp %s/systemd/alphaipi-web.service /etc/systemd/system/alphaipi-web.service" % PROJ, sudo=True)
sh(cli, "systemctl daemon-reload", sudo=True)
sh(cli, "systemctl enable alphaipi-web", sudo=True)
sh(cli, "systemctl restart alphaipi-web", sudo=True)
sh(cli, "sleep 2; systemctl is-active alphaipi-web", sudo=True)
sh(cli, "curl -s -o /dev/null -w 'HTTP=%{http_code}\\n' http://127.0.0.1:8080/ || true")
sh(cli, "hostname -I")
sh(cli, "find %s -maxdepth 3 -type f | sort" % BASE)
cli.close()
print("done")
