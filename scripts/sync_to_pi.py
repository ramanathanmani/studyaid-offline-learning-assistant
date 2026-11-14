import os, sys, stat
from pathlib import Path
import paramiko

root = Path(__file__).resolve().parent.parent

def sftp_sync(sftp, local_dir, remote_dir):
    try:
        sftp.mkdir(remote_dir)
    except IOError:
        pass

    for item in os.listdir(local_dir):
        if item in [".git", "__pycache__", ".venv", "books", "dev.0.log", "dev.1.log", "hold.0.log", "hold.1.log"]:
            continue
        if item.endswith(".pdf") or item.endswith(".pte") or item.endswith(".jsonl"):
            continue

        l_path = os.path.join(local_dir, item)
        r_path = f"{remote_dir}/{item}"

        if os.path.isdir(l_path):
            sftp_sync(sftp, l_path, r_path)
        else:
            sftp.put(l_path, r_path)
            mode = os.stat(l_path).st_mode
            try:
                sftp.chmod(r_path, mode)
            except Exception:
                pass
            print(f"Synced {item} -> {r_path}")

def main():
    print("Connecting to Raspberry Pi (192.168.102.237)...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("192.168.102.237", username="rock", password="12345678", timeout=10)
    sftp = ssh.open_sftp()

    dirs_to_sync = ["studyaid", "eval_kit", "data", "final"]
    for d in dirs_to_sync:
        l_dir = str(root / d)
        r_dir = f"/home/rock/studyaid/{d}"
        if os.path.exists(l_dir):
            print(f"Syncing directory: {d}...")
            sftp_sync(sftp, l_dir, r_dir)

    single_files = ["config.toml", "README.md", ".gitignore"]
    for f in single_files:
        l_f = str(root / f)
        r_f = f"/home/rock/studyaid/{f}"
        if os.path.exists(l_f):
            sftp.put(l_f, r_f)
            print(f"Synced {f}")

    sftp.close()
    ssh.close()
    print("All files synced to Pi successfully!")

if __name__ == "__main__":
    main()
