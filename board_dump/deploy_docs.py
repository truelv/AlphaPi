"""把经验文档同步到树莓派 /home/pi/Codes/。"""
import os
import paramiko

HOST, USER, PWD = "192.168.1.27", "pi", "wangchen"
BASE = "/home/pi/Codes"
LOCAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=PWD, timeout=10)


def sh(cmd, sudo=False):
    if sudo:
        cmd = "echo '%s' | sudo -S bash -lc \"%s\"" % (PWD, cmd.replace('"', '\\"'))
    _, o, e = cli.exec_command(cmd, timeout=30)
    out = o.read().decode("utf-8", "replace").strip()
    err = e.read().decode("utf-8", "replace").strip()
    print("$ %s\n  %s%s" % (cmd, out, (" | ERR " + err) if err else ""))


sh("mkdir -p %s/docs" % BASE)
sh("chmod 755 %s %s/docs" % (BASE, BASE))

sftp = cli.open_sftp()
for local, remote in [
    (os.path.join(LOCAL, "docs", "lessons_learned.md"), BASE + "/docs/lessons_learned.md"),
    (os.path.join(LOCAL, "board_dump", "pi_Codes_README.md"), BASE + "/README.md"),
]:
    with open(local, "rb") as f:
        data = f.read()
    with sftp.open(remote, "wb") as rf:
        rf.write(data)
    print("  -> %s (%d bytes)" % (remote, len(data)))
sftp.close()

sh("find %s -maxdepth 3 -type f | sort" % BASE)
cli.close()
print("done")
