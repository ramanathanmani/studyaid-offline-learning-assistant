import json, time, signal, resource, argparse, random
from pathlib import Path
from adapter import run_one


class TO(Exception):
    pass


def on_alarm(sig, frm):
    raise TO()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("out")
    ap.add_argument("--split", default="dev")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--tmo", type=int, default=300)
    a = ap.parse_args()
    k, n = map(int, a.shard.split("/"))
    with open(a.corpus, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f]
    rows = [r for r in rows if r["split"] == a.split]
    random.Random(11).shuffle(rows)
    rows = [r for i, r in enumerate(rows) if i % n == k]
    if a.limit:
        rows = rows[:a.limit]
    out, done = Path(a.out), set()
    if out.exists():
        with open(out, encoding="utf-8") as f:
            done = {json.loads(l)["id"] for l in f}
    signal.signal(signal.SIGALRM, on_alarm)
    with open(out, "a", encoding="utf-8") as f:
        for i, r in enumerate(rows):
            if r["id"] in done:
                continue
            t0 = time.time()
            rec = {"id": r["id"], "ok": True, "err": ""}
            signal.alarm(a.tmo)
            try:
                rec["out"] = run_one(r["text"])
            except TO:
                rec["ok"], rec["err"] = False, "timeout"
            except Exception as e:
                rec["ok"], rec["err"] = False, repr(e)[:200]
            signal.alarm(0)
            rec["secs"] = round(time.time() - t0, 2)
            rec["rss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            print(i + 1, "/", len(rows), r["id"], rec["secs"], "s", "ok" if rec["ok"] else rec["err"])


if __name__ == "__main__":
    main()
