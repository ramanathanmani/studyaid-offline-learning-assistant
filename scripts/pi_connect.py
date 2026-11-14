import os
import sys
import argparse
import paramiko
import time

def test_ssh(ip, user, password=None, key_path=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"[SSH] Connecting to {user}@{ip}...")
    try:
        if key_path and os.path.exists(key_path):
            client.connect(ip, username=user, key_filename=key_path, timeout=10)
        else:
            client.connect(ip, username=user, password=password, timeout=10)
        print("[SSH] Connected successfully!")
        
        # Run basic info check
        stdin, stdout, stderr = client.exec_command("uname -m && free -h")
        out = stdout.read().decode().strip()
        print(f"[Pi System Info]:\n{out}\n")
        return client
    except Exception as e:
        print(f"[SSH Error] Could not connect: {e}")
        return None

def exec_cmd(client, cmd, label=None):
    lbl = f"[{label}] " if label else ""
    print(f"{lbl}Running: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    
    # Stream output
    for line in iter(stdout.readline, ""):
        print(line, end="")
    err = stderr.read().decode().strip()
    if err:
        print(f"[stderr] {err}")
    return stdout.channel.recv_exit_status()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ip", required=True, help="IP address of Raspberry Pi")
    p.add_argument("--user", default="pi", help="SSH username (default: pi)")
    p.add_argument("--password", default=None, help="SSH password")
    p.add_argument("--key", default=os.path.expanduser("~/.ssh/id_ed25519"), help="Private key path")
    p.add_argument("--cmd", default=None, help="Custom command to run on Pi")
    args = p.parse_args()

    client = test_ssh(args.ip, args.user, args.password, args.key)
    if client and args.cmd:
        exec_cmd(client, args.cmd)
        client.close()
