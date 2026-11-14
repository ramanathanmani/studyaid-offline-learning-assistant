# StudyAid Finals Runbook: test on textbook paragraphs, score it, then flash and verify on the board

Follow this top to bottom. The board flashing and the laptop testing run **in parallel**, and they meet at the freeze (section 7). Everything stays local. Push to GitHub only after you confirm the final product.

---

## 0. What this gives you, and what it does not

- A repeatable test: textbook PDFs become hundreds of test paragraphs, the pipeline runs on each, and scripts score every output.
- An **accuracy score** made of two parts: (1) automatic checks on every paragraph, and (2) a human-checked sample of about 30 paragraphs.
- A board checklist so that when the Pi is ready, you only copy the frozen build over, run the checks and confirm.

**Limits, stated plainly.** The automatic checks measure grounding and consistency: quiz answers found in the cited sentence, numbers not invented or lost, summary points traceable, Tamil terms matching the glossary, no garbled text. They cannot judge whether an explanation is good teaching. For example, the checks would still pass a simplified sentence that drops the triple-point explanation. The human-checked sample covers that gap. Report both numbers and say which is which.

**Assumptions.** The pipeline runs through the ExecuTorch Python runtime with Llama 3.2 1B SpinQuant INT4. The organiser passage is English text of about 150-300 words. Tamil terms come from `glossary.json`. Your laptop run took about 29 s per passage, which I use for time estimates.

---

## 1. Order of work

| Step | Track | What | Rough time |
|---|---|---|---|
| 1 | Both | Safety copy: commit locally, copy the project, model file, tokenizer and glossary to a USB drive | 10 min |
| 2 | A (board) | Flash and boot the board, run `board_check.sh` (section 2) | 30-60 min, in parallel |
| 3 | B (laptop) | Put the PDFs in `books/`, build the corpus, read 20 paragraphs by eye (section 3) | 25 min |
| 4 | B | Wire `adapter.py`, smoke test on 5 paragraphs (section 5) | 15 min |
| 5 | B | Dev run on 100 paragraphs, then fix, rerun (sections 6, 7) | about 50 min per 100 paragraphs, 1-3 rounds |
| 6 | B | Freeze, run the hold-out once, do the human check (sections 7, 8) | about 50 min + 30 min |
| 7 | A | Copy the frozen build to the board, validate on the board (section 9) | 45-60 min |
| 8 | Both | Demo package and two rehearsals (section 10) | 30 min |

At about 29 s per paragraph, 100 paragraphs take roughly 50 minutes. Measure your own speed on the first 5 and recompute.

**If time is short, cut in this order:** the Class 10 or social science books first, then the dev run size (down to 60), then the second fix round. Never cut the hold-out run, the human check, the board validation or the offline capture.

**If you use the orchestrator, sub-agents and verifier:** the orchestrator owns this runbook. One sub-agent builds the corpus and runs the dev tier. One handles board bring-up notes. One investigates failure clusters. The verifier runs `report.py` on the hold-out and signs off against section 8, and it should never see which paragraphs were used for fixing.

---

## 2. Track A: board bring-up

### 2.1 Flash
1. If the organisers gave an image or setup instructions for the board, use those first. They know what the boards need.
2. Otherwise use Raspberry Pi Imager and choose **Raspberry Pi OS (64-bit)**. The Lite version leaves more RAM for the model. In the Imager settings, set the username, enable SSH, and add Wi-Fi for setup only.
3. Use a fast SD card of 32 GB or more.
4. Check the board's RAM before anything else. Your model run peaked at about 1.9 GB.

### 2.2 First boot check
Copy `board_check.sh` over and run it:

```bash
#!/bin/bash
echo "arch:     $(uname -m)"
echo "os:       $(. /etc/os-release; echo $PRETTY_NAME)"
echo "glibc:    $(ldd --version | head -1)"
echo "python:   $(python3 --version)"
echo "ram:      $(free -m | awk '/Mem:/ {print $2" MB total, "$7" MB available"}')"
echo "disk:     $(df -h / | awk 'NR==2 {print $4" free"}')"
echo "cores:    $(nproc)"
echo "temp:     $(vcgencmd measure_temp 2>/dev/null)"
echo "throttle: $(vcgencmd get_throttled 2>/dev/null)"
echo "governor: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)"
echo "route:    $(ip route | grep default || echo none)"
python3 -c "import executorch; print('executorch: import ok')" 2>&1 | tail -1
```

What to look for:

| Line | Good | If not |
|---|---|---|
| arch | `aarch64` | You flashed a 32-bit image. Reflash. |
| python | In the range your ExecuTorch version supports (the ExecuTorch docs list 3.10 to 3.13 for recent releases; check the docs for your version) | Use a venv with a supported Python |
| ram | At least 4 GB total | A 2 GB board is unlikely to hold the model |
| throttle | `throttled=0x0` | Under-voltage or heat. Use the official power supply and cooling |
| governor | `performance` | See 2.4 |
| executorch | `import ok` | See 2.3 |

### 2.3 Getting the ExecuTorch Python runtime working
Climb this ladder and stop at the first rung that works. Run a one-paragraph smoke test after each rung.

1. **Ask the organisers** what environment is already on the board. They said to use Python, so a working setup is likely provided.
2. **Install the same ExecuTorch version you used on the laptop** into a fresh venv. A GitHub issue I found reported that PyPI had no aarch64 build for the Raspberry Pi 5 at that time, so this may fail. Check for yourself.
3. **Copy a ready-made environment or wheel** from the organisers or a teammate, if one exists.
4. **Use the compiled runner binary** from the ExecuTorch Raspberry Pi tutorial and call it from your adapter through `subprocess`. This needs a different adapter on the board, so rerun the board check afterwards.
5. **Build from source on the board.** This is slow, so treat it as the last resort.

### 2.4 Performance settings
- Set the CPU governor to performance: `echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
- Use active cooling and the official power supply. Check `vcgencmd get_throttled` again after a long run.
- Set the model's thread count explicitly to the number of cores (`nproc`), and write the number in your report. Your laptop run used 8 cores, and the Pi has fewer.

### 2.5 Offline mode
Before the final capture: unplug ethernet, then turn Wi-Fi off with `nmcli radio wifi off` (or `rfkill block wifi`). Confirm that `ip route` shows no default route. Then run the telemetry. It must say `Offline status: OFFLINE`.

---

## 3. Build the test corpus from the PDFs

### 3.1 File names
Scope note: only Class 9 books are available, so tests and glossary cover Class 9 only. A book-scout agent finds the PDFs under `/home/rock/Downloads/Class 9 Books/`, copies them into `books/` with these names and writes `books_inventory.md`.

Put the English-medium PDFs in `books/` named `CLASS_SUBJECT_TERM_en.pdf`, for example `8_sci_1_en.pdf`, `9_sci_2_en.pdf`, `10_math_1_en.pdf`. Put each Tamil-medium twin next to it as `8_sci_1_ta.pdf`. The English books provide the test paragraphs. The Tamil books are used to check the Tamil terms.

### 3.2 Build it
```
python corpus.py books/ corpus.jsonl
```
This extracts the text with `pdftotext`, drops exercises, figure captions and tables, builds passages of 150-300 words that start at sentence boundaries, removes duplicates, and splits them into **dev (70%)** and **hold-out (30%)**. The split is made on blocks of 40 neighbouring paragraphs, so a hold-out paragraph never has a near-identical neighbour in dev. Never use hold-out results to make fixes.

### 3.3 Read 20 paragraphs yourself (do not skip)
```
python -c "import json,random; r=[json.loads(l) for l in open('corpus.jsonl',encoding='utf-8')]; [print(x['id'],'\n',x['text'][:500],'\n') for x in random.sample(r,20)]"
```
Check that they read like real passages, start and end cleanly, and are not lists, tables or exercises. If many are bad, change `LO`, `HI` or the `BAD` pattern in `corpus.py` and rebuild. If the Tamil twin text looks garbled, the Tamil check will not work for that book. OCR it or leave it out.

### 3.4 Keep 2-3 books out of the glossary (honest coverage)
Your glossary is built from these same books, so testing on them gives flattering Tamil coverage. To measure how the glossary does on unseen text, build a copy of the glossary **without** 2-3 books (for example one science and one maths book), and test those books against that copy. Report that number as the honest coverage. The final glossary you ship uses all books.

---

## 4. What the score checks

Each paragraph is scored on these checks. The weights make up a score out of 100.

| Check (weight) | Passes when | Cannot catch |
|---|---|---|
| run (10) | No crash, no timeout, output is complete | |
| quiz (25) | At least 3 questions, each with a real cited sentence containing the answer, no duplicates, the answer not given away in the question, 3+ distinct options if options exist | A question that is valid but trivial or badly worded |
| summ (20) | At least 3 points, each citing real sentences, mostly made of words from those sentences, no numbers that are not in the passage | A point that is traceable but misleading |
| simp (15) | The hard sentence's numbers are kept, enough of its key words survive, and the sentences are not longer than the original | Dropped explanations, as in your first run |
| gloss (20) | Every term shown is in the passage, has a Tamil entry matching `glossary.json`, no "English only" for terms the glossary knows, and at least 60% of the glossary terms in the passage are covered (up to 5) | A correct-looking Tamil term that is wrong in the glossary itself |
| exam (5) | The example comes from your local example bank | |
| fmt (5) | No garbled characters such as `\ufffd` or UTF-8 text decoded wrongly | |
| nums (gate) | No number appears in the output that is not in the passage, and the hard sentence's numbers are preserved | |

Reported results:
- **Pass rate per check**, so you see exactly what is weak.
- **Mean weighted score** out of 100.
- **Strict pass**: the share of paragraphs that pass every check, with a 95% confidence interval. With fewer than about 100 paragraphs the interval is wide, so run more before you trust a number.
- **Time per paragraph** (median and 95th percentile) and peak memory.

### 4.1 Human-checked sample (the real accuracy number)
`report.py --gold 30` writes `gold.csv` with 30 random paragraphs. Two people (you and a teammate) read each output next to its passage and tick yes or no per column:

| Column | Yes means |
|---|---|
| simple_ok | The simplified sentence keeps the full meaning and is easier to read |
| summary_ok | The summary is correct and complete enough |
| quiz_ok | Questions are sensible and the marked answers are right |
| tamil_terms_ok | The Tamil terms are correct. Check them with a Tamil speaker, or search the term in the Tamil textbook PDF |

Human accuracy per column is the number of yes ticks divided by 30. Note any disagreement between the two people.

*Optional, for testing only:* on the laptop you may ask a stronger AI model to review a sample of outputs for meaning errors. That helps you find problems faster, but it never replaces the human check and it is never part of the offline product.

---

## 5. The test kit

Files are in the `eval_kit/` folder next to this file. The code is also listed here so the runbook stands alone.

### 5.1 `adapter.py` (you connect this to your pipeline)
Replace `pipeline.process` with your real entry point. Two rules: **load the model once** outside `run_one` (otherwise every paragraph pays the loading time), and return exactly these keys.

| Key | Meaning |
|---|---|
| `sents` | The passage sentences, in your own numbering (S1 is the first item) |
| `hard` | The 1-based number of the sentence you simplified |
| `simple` | The simplified text (a string or a list of strings) |
| `summary` | List of `{"txt": ..., "cite": [sentence numbers]}` |
| `terms` | List of `{"en": ..., "ta": ...}`. Use an empty `ta` when the glossary has no entry |
| `quiz` | List of `{"q": ..., "opts": [...], "ans": index, "cite": sentence number}`. If you have no options yet, use `"a"` for the answer text instead |
| `example` | `{"id": ..., "txt": ...}` from your example bank, or `None` |

```python
from pipeline import process


def run_one(txt):
    o = process(txt)
    return {
        "sents": o["sents"],
        "hard": o["hard"],
        "simple": o["simple"],
        "summary": o["summary"],
        "terms": o["terms"],
        "quiz": o["quiz"],
        "example": o.get("example"),
    }
```

### 5.2 `corpus.py`
```python
import re, json, sys, hashlib, subprocess
from pathlib import Path

LO, HI = 150, 300
BAD = re.compile(r"^(activity|exercise|fig|figure|table|note|do you know|think|let us|evaluate|choose|fill|match|answer)\b", re.I)


def pdf_txt(p):
    r = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True)
    return r.stdout


def clean(t):
    t = t.replace("\u00ad", "").replace("\x0c", "\n\n")
    return re.sub(r"-\n(?=[a-z])", "", t)


def paras(t):
    out = []
    for b in re.split(r"\n\s*\n", clean(t)):
        b = " ".join(b.split())
        if b:
            out.append(b)
    return out


def bad(p):
    if len(p.split()) < 12 or BAD.match(p):
        return True
    al = sum(c.isalpha() or c == " " for c in p) / len(p)
    return al < 0.82


def wc(xs):
    return sum(len(x.split()) for x in xs)


def sents_of(p):
    return re.split(r"(?<=[.!?])\s+(?=[A-Z(])", p)


def split_big(p):
    out, buf, n = [], [], 0
    for s in sents_of(p):
        buf.append(s)
        n += len(s.split())
        if n >= LO:
            out.append(" ".join(buf))
            buf, n = [], 0
    return out


def windows(ps):
    buf = []
    for p in ps:
        if bad(p):
            buf = []
            continue
        if len(p.split()) > HI:
            buf = []
            yield from split_big(p)
            continue
        buf.append(p)
        if wc(buf) > HI:
            buf = [p]
        if wc(buf) >= LO:
            yield " ".join(buf)
            buf = []


def nsent(t):
    return len(re.split(r"(?<=[.!?])\s+", t.strip()))


def meta(name):
    m = re.match(r"(\d+)_([a-z]+)_(\d+)_en\.pdf$", name)
    return m.groups() if m else None


def build(d, out):
    seen, rows = set(), []
    for p in sorted(Path(d).glob("*_en.pdf")):
        m = meta(p.name)
        if not m:
            print("skip, bad name:", p.name)
            continue
        ta = p.with_name(p.name[:-6] + "ta.pdf")
        i = 0
        for w in windows(paras(pdf_txt(p))):
            key = hashlib.md5(" ".join(w.lower().split()).encode()).hexdigest()
            if key in seen or nsent(w) < 5:
                continue
            seen.add(key)
            h = int(hashlib.md5(f"{p.name}:{i // 40}".encode()).hexdigest(), 16) % 10
            rows.append({
                "id": f"{p.stem}_{i:04d}", "text": w, "words": len(w.split()),
                "cls": m[0], "subj": m[1], "term": m[2],
                "ta_book": str(ta) if ta.exists() else "",
                "split": "hold" if h < 3 else "dev",
            })
            i += 1
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tot = {}
    for r in rows:
        k = (r["subj"], r["split"])
        tot[k] = tot.get(k, 0) + 1
    print(len(rows), "paragraphs", tot)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
```

### 5.3 `run_eval.py`
Runs the pipeline over the corpus, writes one line per paragraph, can resume after a crash, shuffles with a fixed seed so any `--limit` sample mixes all books, and supports shards. A timeout only interrupts when control returns to Python, so a hang inside the native runtime may still block until it finishes.

```python
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
```

### 5.4 `checks.py`
```python
import re, json

NUM = re.compile(r"\d+(?:\.\d+)?")
WRD = re.compile(r"[a-z0-9]+")
TAMIL = re.compile(r"[\u0B80-\u0BFF]")
STOP = set("the and for are was were with that this from have has had not but can may will its their there which when what where also into than then them they been being such these those other each only some most more over under about after before between because while during".split())
W = {"run": 10, "quiz": 25, "summ": 20, "simp": 15, "gloss": 20, "exam": 5, "fmt": 5}


def nums(t):
    return set(NUM.findall(t))


def toks(t):
    return [w for w in WRD.findall(t.lower()) if w not in STOP]


def cover(a, b):
    ta = set(toks(a))
    if not ta:
        return 0.0
    return len(ta & set(toks(b))) / len(ta)


def ans_txt(q):
    op, i = q.get("opts"), q.get("ans")
    if op and isinstance(i, int) and 0 <= i < len(op):
        return op[i]
    return q.get("a", "")


def okc(c, n):
    return isinstance(c, int) and 1 <= c <= n


def quiz_ok(o, sents):
    qs = o.get("quiz") or []
    good, seen = 0, set()
    for q in qs:
        t, a, c = q.get("q", "").strip(), ans_txt(q), q.get("cite")
        if not t or not a or t.lower() in seen:
            continue
        seen.add(t.lower())
        if not okc(c, len(sents)) or cover(a, sents[c - 1]) < 0.6 or cover(a, t) > 0.8:
            continue
        op = q.get("opts")
        if op and (len(op) < 3 or len(set(op)) != len(op)):
            continue
        good += 1
    return len(qs) >= 3 and good >= 3


def summ_ok(o, sents, txt):
    pts = o.get("summary") or []
    if len(pts) < 3:
        return False
    base = nums(txt)
    for p in pts:
        cs = p.get("cite") or []
        if not cs or not all(okc(c, len(sents)) for c in cs):
            return False
        src = " ".join(sents[c - 1] for c in cs)
        if cover(p.get("txt", ""), src) < 0.4 or nums(p.get("txt", "")) - base:
            return False
    return True


def nsents(t):
    return max(1, len(re.split(r"(?<=[.!?])\s+", t.strip())))


def simp_ok(o, sents):
    s, h = o.get("simple") or "", o.get("hard")
    if isinstance(s, list):
        s = " ".join(s)
    if not s or not okc(h, len(sents)):
        return False
    orig = sents[h - 1]
    if not nums(orig) <= nums(s) or cover(orig, s) < 0.5:
        return False
    return len(s.split()) / nsents(s) <= len(orig.split())


def nums_ok(o, sents, txt):
    s = o.get("simple") or ""
    if isinstance(s, list):
        s = " ".join(s)
    blob = s
    for p in o.get("summary") or []:
        blob += " " + p.get("txt", "")
    for q in o.get("quiz") or []:
        blob += " " + q.get("q", "") + " " + ans_txt(q)
    h = o.get("hard")
    keep = not okc(h, len(sents)) or nums(sents[h - 1]) <= nums(s)
    return keep and not (nums(blob) - nums(txt))


def gloss_ok(o, txt, gl, tab):
    ts = o.get("terms") or []
    low = txt.lower()
    known = [t for t in gl if re.search(r"\b" + re.escape(t) + r"s?\b", low)]
    if not ts:
        return not known, 1.0 if not known else 0.0
    shown = set()
    for t in ts:
        en, ta = t.get("en", "").lower(), t.get("ta") or ""
        if not re.search(r"\b" + re.escape(en) + r"s?\b", low):
            return False, 0.0
        if en in gl:
            if ta != gl[en].get("ta"):
                return False, 0.0
            shown.add(en)
        elif ta:
            return False, 0.0
    cov = len(shown) / min(5, len(known)) if known else 1.0
    return cov >= 0.6, min(cov, 1.0)


def fmt_ok(o):
    b = json.dumps(o, ensure_ascii=False)
    return "\ufffd" not in b and "\u00e0\u00ae" not in b and "\u00e0\u00af" not in b


def score_one(rec, row, gl, bank, tab):
    r = dict.fromkeys(list(W) + ["nums"], False)
    r["run"] = bool(rec.get("ok")) and bool(rec.get("out"))
    if not r["run"]:
        return r
    o, txt = rec["out"], row["text"]
    sents = o.get("sents") or []
    r["quiz"] = quiz_ok(o, sents)
    r["summ"] = summ_ok(o, sents, txt)
    r["simp"] = simp_ok(o, sents)
    r["nums"] = nums_ok(o, sents, txt)
    r["gloss"], r["cov"] = gloss_ok(o, txt, gl, tab)
    r["exam"] = True if bank is None else (o.get("example") or {}).get("id") in bank
    r["fmt"] = fmt_ok(o)
    return r


def total(r):
    return sum(W[k] for k in W if r.get(k))


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (c - m) / d, (c + m) / d
```

### 5.5 `report.py`
```python
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
```

I tested these scripts on the temperature passage with a fake adapter, and on a generated PDF. A good output scored 100 and a copy of your first run's output (2 quiz questions, a single-line summary, "English only" glossary, invented example) scored 30. That is a check of the scripts, not of your pipeline, so expect to fix small false alarms in the checks during your first run.

---

## 6. Running it on the laptop

Do these in order, and stop to fix when a step fails.

| Tier | Command | Paragraphs | Purpose |
|---|---|---|---|
| Smoke | `python run_eval.py corpus.jsonl smoke.jsonl --split dev --limit 5` | 5 | Adapter works, output keys are right |
| Dev | `python run_eval.py corpus.jsonl dev.jsonl --split dev --limit 100` | 100 | Find and fix problems |
| Hold-out | `python run_eval.py corpus.jsonl hold.jsonl --split hold --limit 100` | 100 | The score you report. Run once, after freeze |

Score any of them with:
```
python report.py corpus.jsonl "dev.jsonl" glossary.json --bank example_bank.json
```
Drop `--bank` if you have no example bank yet.

**Speeding up.** The laptop has 8 cores and 14 GB of RAM. You can try two parallel shards, each with its own output file, but test it first because both runs share the CPU:
```
python run_eval.py corpus.jsonl dev.0.jsonl --split dev --shard 0/2 --limit 100
python run_eval.py corpus.jsonl dev.1.jsonl --split dev --shard 1/2 --limit 100
python report.py corpus.jsonl "dev.*.jsonl" glossary.json
```
Do not use parallel runs for timing numbers.

---

## 7. Fix loop and freeze

### 7.1 Fix loop (dev only)
1. Open `eval_report.md` and find the check with the lowest pass rate.
2. Read 10 failing outputs for that check by hand. Decide whether the **pipeline** is wrong or the **check** is wrong.
3. Fix the root cause (the prompt, the glossary, the validation or the fallback), not the single paragraph.
4. Rerun only the failing paragraphs plus 20 that passed, to catch regressions. Rerun the full dev set when the quick rerun is clean.
5. Do at most 3 rounds.
6. If a check is wrongly failing good outputs, fix the check and write down the change. Never loosen a threshold just to reach a target.

Likely first failures, from your earlier run: fewer than 3 quiz questions (fallback not firing), "English only" in the glossary, the invented example, a one-line summary, and a simplified sentence that dropped the definition.

### 7.2 Freeze
When dev looks good, freeze:
- `git add -A && git commit -m "finals freeze" && git tag finals-freeze` (local only, no push)
- Write down `git rev-parse --short HEAD`, the model file's `sha256sum` and size, and the number of glossary entries.
- From now on only fix real crashes. Any change means rerunning the hold-out.

### 7.3 Hold-out run
Run the hold-out once on the frozen build and keep `eval_report.md` as `final_report_laptop.md`. Do the human check (4.1) on 30 paragraphs from it.

---

## 8. Release gates

These are my suggested targets for the hold-out. Adjust them if your early runs show checker false alarms, and write down any change.

| Measure | Target |
|---|---|
| Crashes and timeouts | 0 |
| quiz pass rate | at least 95% |
| nums (no invented or lost numbers) | 100% (investigate every failure) |
| gloss pass rate | at least 95%, and no "English only" for known terms |
| summ and simp pass rates | at least 90% each |
| fmt (no garbled text) | 100% |
| Mean weighted score | at least 90 |
| Strict pass rate | at least 85%. If the lower end of its 95% interval is under 75%, test more paragraphs |
| Human-checked accuracy | at least 85% in each column |
| Tamil terms (human check) | no wrong term left in the demo passages |
| Honest glossary coverage (3.4) | report it, whatever it is |

If a gate fails, go back to 7.1 on dev. If time has run out, ship what you have and describe the weak spot honestly in your submission.

---

## 9. On the board

Start only after the freeze and the hold-out run.

### 9.1 Bundle
Put these on the USB drive: the frozen project folder (at the `finals-freeze` tag), the model `.pte`, the tokenizer, `glossary.json`, `example_bank.json`, `eval_kit/`, 30 test paragraphs (copy the gold sample from `corpus.jsonl` into a small `board_corpus.jsonl`), and a `checksums.txt` made with `sha256sum`. On the board, run `sha256sum -c checksums.txt` to confirm nothing was damaged.

### 9.2 Validation steps
| Step | What to do | Pass when |
|---|---|---|
| 1 | `board_check.sh` | arch is aarch64, no throttling, runtime imports |
| 2 | One paragraph, **cold** (first run after boot), then the same paragraph again, **warm** | Both complete. Record both times, since the first run loads the model file from disk |
| 3 | Run the 30 board paragraphs through `run_eval.py` and `report.py` | No crashes, and the strict pass rate is within 2 failing paragraphs of the laptop result on the same 30 |
| 4 | Compare with the laptop | Differences are small. The quantised model can give slightly different text on different hardware, so compare scores, not exact words |
| 5 | Soak test: 10 paragraphs in a row | No crash, memory not steadily growing, temperature below throttling |
| 6 | Wi-Fi off (2.5), run the organiser passage | `Offline status: OFFLINE`, telemetry complete |
| 7 | Time budget | Decide whether the live demo uses the model's measured speed. If a run is too slow for the demo, show a pre-recorded output from the same commit and say so |

Save the board outputs and telemetry from steps 2, 3 and 6 for your submission.

### 9.3 If something fails on the board
| Symptom | First thing to try |
|---|---|
| Runtime will not import | The ladder in 2.3 |
| `GLIBC_x.xx not found` | The binary was built on a newer system than the board. Use a newer OS image or rebuild on the board's system |
| Out of memory | Close other programs, use Lite, check the board's RAM |
| Much slower than expected | Check throttling, the governor and the thread count |
| Garbled Tamil in the terminal | Set a UTF-8 locale (`locale`) and use a terminal font with Tamil support |
| Nothing works in time | Run on the laptop and say so |

---

## 10. Final package and fallbacks

Show the judges, in this order:
1. The hard sentence from the organiser passage.
2. The offline run on the board: simple version, Tamil terms, quiz, summary.
3. The telemetry: model, size, memory, inference time, offline status.
4. The score slide: strict pass rate with its interval on N hold-out paragraphs, human-checked accuracy on 30, honest glossary coverage, and one sentence on what the score does not measure.
5. The student impact example.

Fallback ladder, with the live run first:
1. Live run on the board.
2. A saved offline run from the same commit (`demo_output_offline.txt`).
3. Live run on the laptop.

Always tell the judges which one they are seeing.

Keep the final package local until you review it and confirm. Only then push once. Before pushing, check that the repo does not contain the model file or the textbook PDFs.

---

## 11. Tick list

- [ ] Project, model, tokenizer and glossary copied to USB
- [ ] Board flashed, `board_check.sh` clean, runtime imports
- [ ] PDFs named correctly in `books/`, corpus built, 20 paragraphs read by eye
- [ ] 2-3 books held out of the test glossary
- [ ] `adapter.py` connected, model loaded once, smoke test passes
- [ ] Dev run, fix loop done (at most 3 rounds)
- [ ] Freeze: commit, tag, model checksum noted
- [ ] Hold-out run saved as `final_report_laptop.md`
- [ ] Human check on 30 paragraphs, Tamil terms checked
- [ ] Gates in section 8 reviewed
- [ ] Bundle copied to the board, checksums verified
- [ ] Cold and warm runs recorded, 30-paragraph board run done, soak test done
- [ ] Wi-Fi off, `Offline status: OFFLINE` captured
- [ ] Demo rehearsed twice, fallback ladder ready
- [ ] You confirm the final product, then push once
