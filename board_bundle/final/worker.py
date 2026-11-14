import sys, os, json, time, resource
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "eval_kit"))
sys.path.insert(0, str(root))

from adapter import run_one

def main():
    sys.stdout.write("STUDYAID_READY\n")
    sys.stdout.flush()

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        req = json.loads(line)
        jid = req.get("id")
        txt = req.get("text", "")
        t0 = time.time()
        res = {"id": jid, "ok": True, "err": "", "result": None}
        try:
            out = run_one(txt)
            res["result"] = out
        except Exception as e:
            res["ok"] = False
            res["err"] = repr(e)[:200]
        res["elapsed_s"] = round(time.time() - t0, 2)
        res["rss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
        sys.stdout.write("STUDYAID_RES:" + json.dumps(res, ensure_ascii=False) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
