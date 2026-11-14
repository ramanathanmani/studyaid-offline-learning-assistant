import json, sys, glob, argparse, csv, random, subprocess
from checks import score_one, total, wilson, W
from corpus import pdf_txt


def load(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def pct(x, n):
    return round(100 * x / n, 1) if n else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("results")
    ap.add_argument("glossary")
    ap.add_argument("--bank", default="")
    ap.add_argument("--gold", type=int, default=0)
    ap.add_argument("--out", default="eval_report.md")
    a = ap.parse_args()
    rows = {r["id"]: r for r in load(a.corpus)}
    recs = []
    for p in sorted(glob.glob(a.results)):
        recs += load(p)
    with open(a.glossary, encoding="utf-8") as f:
        gl = json.load(f)
    bank = None
    if a.bank:
        with open(a.bank, encoding="utf-8") as f:
            bank = set(json.load(f))
    tabs = {}
    res = []
    for rec in recs:
        row = rows.get(rec["id"])
        if not row:
            continue
        bk = row["ta_book"]
        if bk and bk not in tabs:
            tabs[bk] = pdf_txt(bk)
        s = score_one(rec, row, gl, bank, tabs.get(bk, ""))
        s["id"], s["secs"], s["rss"] = rec["id"], rec.get("secs", 0), rec.get("rss", 0)
        s["err"] = rec.get("err", "")
        s["score"] = total(s)
        res.append(s)
    n = len(res)
    if not n:
        print("no results")
        return
    keys = list(W) + ["nums"]
    strict = sum(all(r[k] for k in keys) for r in res)
    lo, hi = wilson(strict, n)
    secs = sorted(r["secs"] for r in res if r["run"])
    p50 = secs[len(secs) // 2] if secs else 0
    p95 = secs[int(len(secs) * 0.95) - 1] if len(secs) > 1 else p50
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:
        sha = ""
    L = [f"# Eval report", "", f"commit: {sha or 'n/a'}  |  paragraphs: {n}", ""]
    L += ["| Check | Pass % |", "|---|---|"]
    for k in keys:
        L.append(f"| {k} | {pct(sum(r[k] for r in res), n)} |")
    L += ["", f"Mean weighted score: **{round(sum(r['score'] for r in res) / n, 1)} / 100**", ""]
    L += [f"Strict pass (all checks): **{pct(strict, n)}%**  (95% interval {round(100 * lo, 1)} to {round(100 * hi, 1)})", ""]
    L += [f"Time per paragraph: p50 {p50}s, p95 {p95}s  |  peak RSS {max(r['rss'] for r in res)} MiB", ""]
    L += ["## Failing ids (first 15 per check)", ""]
    for k in keys:
        bad = [r["id"] for r in res if not r[k]][:15]
        if bad:
            L.append(f"- {k}: " + ", ".join(bad))
    errs = {}
    for r in res:
        if r["err"]:
            errs[r["err"][:60]] = errs.get(r["err"][:60], 0) + 1
    if errs:
        L += ["", "## Errors", ""] + [f"- {v} x {k}" for k, v in errs.items()]
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    if a.gold:
        random.seed(7)
        pick = random.sample(recs, min(a.gold, len(recs)))
        with open("gold.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "simple_ok", "summary_ok", "quiz_ok", "tamil_terms_ok", "notes"])
            for r in pick:
                w.writerow([r["id"], "", "", "", "", ""])
        print("wrote gold.csv for", len(pick), "paragraphs")


if __name__ == "__main__":
    main()
