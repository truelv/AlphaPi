"""在树莓派上执行命令 / 上传并运行本地脚本。
用法：
    python pi_run.py "<命令>" [--sudo]
    python pi_run.py --file <本地脚本.py> [--sudo]
"""
import os
import sys
import paramiko

HOST, USER, PWD = "192.168.1.27", "pi", "wangchen"

args = sys.argv[1:]
use_sudo = "--sudo" in args
if use_sudo:
    args.remove("--sudo")

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=PWD, timeout=10)

if args and args[0] == "--file":
    local = args[1]
    remote = "/tmp/" + os.path.basename(local)
    sftp = cli.open_sftp()
    with open(local, "rb") as f:
        data = f.read()
    with sftp.open(remote, "wb") as rf:
        rf.write(data)
    sftp.close()
    cmd = "python3 " + remote
else:
    cmd = args[0]

if use_sudo:
    cmd = "echo '%s' | sudo -S bash -lc \"%s\"" % (PWD, cmd.replace('"', '\\"'))

_, o, e = cli.exec_command(cmd, timeout=60)
out = o.read().decode("utf-8", "replace")
err = e.read().decode("utf-8", "replace")
print(out)
if err.strip():
    print("--- stderr ---")
    print(err)
cli.close()
