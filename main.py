#!/usr/bin/env python3
"""ExcelPilot 启动器：终端窗口就是服务本体，Ctrl+C 或关窗口即停止。"""

import os
import socket
import subprocess
import sys
import urllib.request
import webbrowser

PORT_START = int(os.environ.get("EXCELPILOT_PORT", "8765"))


def running_port():
    """已在服务的 ExcelPilot 端口，没有则 0"""
    for port in range(PORT_START, PORT_START + 30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                continue
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as resp:
                if "ExcelPilot" in resp.read(8192).decode("utf-8", "replace"):
                    return port
        except OSError:
            pass
    return 0


def main():
    print("正在启动 ExcelPilot ...", flush=True)
    port = running_port()
    if port:
        print(f"ExcelPilot 已在运行：http://127.0.0.1:{port}")
        webbrowser.open(f"http://127.0.0.1:{port}")
        print("要停止请到它的窗口按 Ctrl+C，本窗口可以直接关掉")
        return 0

    # 不加 PIPE、继承终端 stdio：日志实时可见，Ctrl+C 与关窗口会连同子进程一起终止
    proc = subprocess.Popen([sys.executable, "-m", "excelpilot"])
    try:
        return proc.wait()
    except KeyboardInterrupt:
        try:
            proc.wait(timeout=5)   # Ctrl+C 同时送达子进程，等它自己退出
        except subprocess.TimeoutExpired:
            proc.kill()
        return 0


if __name__ == "__main__":
    sys.exit(main())
