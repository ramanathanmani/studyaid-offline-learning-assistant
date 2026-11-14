import os, sys, time, json, queue, threading, subprocess, socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

root = Path(__file__).resolve().parent.parent
web_dir = Path(__file__).resolve().parent / "web"
pte_path = root / "models/llama1b/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte"

jobs = {}
job_q = queue.Queue()
lock = threading.Lock()
worker_proc = None
worker_ready = False
current_job = None
last_run_telemetry = None

def get_offline_status():
    try:
        r = subprocess.run(["ip", "route"], capture_output=True, text=True, timeout=1)
        has_default = "default via" in r.stdout
        return not has_default, "OFFLINE" if not has_default else "ONLINE"
    except Exception:
        return True, "OFFLINE"

def get_host_info():
    uname = os.uname()
    is_pi = "rpi" in uname.release.lower() or "aarch64" in uname.machine.lower()
    label = "Raspberry Pi 5 (ARM64)" if is_pi else f"Laptop ({uname.machine})"
    return {"machine": uname.machine, "release": uname.release, "is_pi": is_pi, "label": label}

def start_worker():
    global worker_proc, worker_ready
    worker_ready = False
    worker_script = Path(__file__).resolve().parent / "worker.py"
    env = os.environ.copy()
    env["STUDYAID_THREADS"] = "4"
    worker_proc = subprocess.Popen(
        [sys.executable, "-u", str(worker_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        env=env
    )
    while True:
        line = worker_proc.stdout.readline()
        if not line:
            break
        if "STUDYAID_READY" in line:
            worker_ready = True
            break

def worker_supervisor():
    global worker_proc, worker_ready, current_job, last_run_telemetry
    start_worker()
    while True:
        try:
            jid, txt = job_q.get()
            with lock:
                current_job = jid
                jobs[jid]["stage"] = "working"
                jobs[jid]["start_time"] = time.time()

            req_line = json.dumps({"id": jid, "text": txt}) + "\n"
            worker_proc.stdin.write(req_line)
            worker_proc.stdin.flush()

            resp = None
            t_done = time.time()
            while True:
                resp_line = worker_proc.stdout.readline()
                if not resp_line:
                    break
                if resp_line.startswith("STUDYAID_RES:"):
                    payload = resp_line[len("STUDYAID_RES:"):].strip()
                    resp = json.loads(payload)
                    t_done = time.time()
                    break

            if not resp:
                with lock:
                    jobs[jid]["stage"] = "error"
                    jobs[jid]["err"] = "Worker process exited unexpectedly. Restarting."
                    current_job = None
                start_worker()
                job_q.task_done()
                continue
            with lock:
                if resp.get("ok"):
                    jobs[jid]["stage"] = "done"
                    jobs[jid]["result"] = resp.get("result")
                    jobs[jid]["elapsed_s"] = resp.get("elapsed_s")
                    jobs[jid]["rss"] = resp.get("rss")
                    last_run_telemetry = {
                        "elapsed_s": resp.get("elapsed_s"),
                        "rss_mb": resp.get("rss"),
                        "timestamp": round(t_done, 2)
                    }
                else:
                    jobs[jid]["stage"] = "error"
                    jobs[jid]["err"] = resp.get("err", "Processing error")
                current_job = None
            job_q.task_done()
        except Exception as e:
            with lock:
                if current_job and current_job in jobs:
                    jobs[current_job]["stage"] = "error"
                    jobs[current_job]["err"] = repr(e)[:150]
                current_job = None
            try:
                start_worker()
            except Exception:
                pass

class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_HEAD(self):
        self.do_GET()

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, path, mime):
        if not path.exists():
            self.send_error(404, "Not Found")
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        p = u.path

        if p == "/" or p == "/index.html":
            self.serve_file(web_dir / "index.html", "text/html; charset=utf-8")
            return
        elif p == "/style.css":
            self.serve_file(web_dir / "style.css", "text/css; charset=utf-8")
            return
        elif p == "/app.js":
            self.serve_file(web_dir / "app.js", "application/javascript; charset=utf-8")
            return
        elif p.startswith("/fonts/"):
            fname = os.path.basename(p)
            fpath = web_dir / "fonts" / fname
            mime = "font/ttf" if fname.endswith(".ttf") else "font/woff2" if fname.endswith(".woff2") else "text/plain"
            self.serve_file(fpath, mime)
            return
        elif p == "/api/status":
            off, off_txt = get_offline_status()
            host = get_host_info()
            pte_sz = pte_path.stat().st_size if pte_path.exists() else 0
            q_len = job_q.qsize() + (1 if current_job else 0)
            st = {
                "host": host["label"],
                "is_pi": host["is_pi"],
                "model": "Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8",
                "pte_size_bytes": pte_sz,
                "threads": 4,
                "offline": off,
                "offline_status": off_txt,
                "model_loaded": worker_ready,
                "queue_len": q_len,
                "last_run": last_run_telemetry
            }
            self.send_json(st)
            return
        elif p == "/api/passages":
            pass_p = Path(__file__).resolve().parent / "passages.json"
            if pass_p.exists():
                with open(pass_p, encoding="utf-8") as f:
                    self.send_json(json.load(f))
            else:
                self.send_json([])
            return
        elif p.startswith("/api/job/"):
            jid = p.split("/api/job/")[1].strip()
            with lock:
                if jid not in jobs:
                    self.send_json({"error": "Job not found"}, 404)
                    return
                j = dict(jobs[jid])
            if j["stage"] == "working" and j.get("start_time"):
                j["elapsed_s"] = round(time.time() - j["start_time"], 1)
            self.send_json(j)
            return
        elif p == "/api/report":
            rep_p = root / "eval_kit/final_report_laptop.md"
            if not rep_p.exists():
                rep_p = root / "eval_kit/eval_report.md"
            if rep_p.exists():
                txt = rep_p.read_text(encoding="utf-8")
                self.send_json({"report": txt, "source": rep_p.name})
            else:
                self.send_json({"error": "Report not found"}, 404)
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/run":
            clen = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(clen).decode("utf-8")
            try:
                body = json.loads(raw)
            except Exception:
                self.send_json({"error": "Invalid JSON"}, 400)
                return

            txt = body.get("text", "").strip()
            words = txt.split()
            if len(words) < 25:
                self.send_json({"error": "Passage is too short. Please provide a textbook paragraph of at least 25 words (recommended 150-300 words)."}, 400)
                return

            jid = f"job_{int(time.time()*1000)}"
            with lock:
                jobs[jid] = {
                    "id": jid,
                    "stage": "queued",
                    "created_at": time.time(),
                    "start_time": None,
                    "elapsed_s": 0.0,
                    "result": None,
                    "err": ""
                }
            job_q.put((jid, txt))
            self.send_json({"job": jid, "stage": "queued"})
            return

        self.send_error(404, "Not Found")

def run_server(host="127.0.0.1", port=8080):
    th = threading.Thread(target=worker_supervisor, daemon=True)
    th.start()
    srv = HTTPServer((host, port), AppHandler)
    print(f"StudyAid server listening at http://{host}:{port}/")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if worker_proc:
            worker_proc.terminate()

if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    run_server(h, p)
