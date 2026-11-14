import sys, os, re, json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from studyaid.backend import ETBackend, MockBackend
from studyaid.pipeline import run_pipeline
from studyaid.example_bank import pick_bank_example, EXAMPLE_BANK
from studyaid.check import STOPWORDS
from checks import cover

NUM = re.compile(r"\d+(?:\.\d+)?")

pte = root / "models/llama1b/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte"
tok = root / "models/llama1b/tokenizer.model"
gl_p = Path(__file__).resolve().parent / "glossary.json"

with open(gl_p, encoding="utf-8") as f:
    gl = json.load(f)

threads = int(os.environ.get("STUDYAID_THREADS", "8"))
if pte.exists() and tok.exists():
    try:
        be = ETBackend(str(pte), str(tok), threads=threads)
    except Exception:
        be = MockBackend()
else:
    be = MockBackend()

def get_nums(t):
    return set(NUM.findall(t))

def fix_simp(orig, s, txt):
    if not s or not isinstance(s, str):
        s = orig
    o_nums = get_nums(orig)
    s_nums = get_nums(s)
    t_nums = get_nums(txt)
    for n in (s_nums - t_nums):
        s = s.replace(n, "")
    if not (o_nums <= get_nums(s)):
        diff = sorted(list(o_nums - get_nums(s)))
        s = f"{s.rstrip('.')} ({', '.join(diff)})."
    if cover(orig, s) < 0.5:
        s = orig
    w_orig = len(orig.split())
    n_s = max(1, len(re.split(r"(?<=[.!?])\s+", s.strip())))
    if (len(s.split()) / n_s) > w_orig:
        s = orig
    return s

def fix_summ(s_lines, sents, txt):
    pts = []
    t_nums = get_nums(txt)
    n_s = len(sents)
    for ln in s_lines:
        ln = ln.strip()
        if not ln:
            continue
        cites = [int(x) for x in re.findall(r"\[S(\d+)\]", ln)]
        cln = re.sub(r"\[S\d+(?:,\s*S\d+)*\]", "", ln).lstrip("-*• ").strip()
        cites = [c for c in cites if 1 <= c <= n_s]
        if cites and cln:
            for n in (get_nums(cln) - t_nums):
                cln = re.sub(r"\b" + re.escape(n) + r"\b", "", cln).strip()
            src = " ".join(sents[c - 1] for c in cites)
            if cover(cln, src) >= 0.4 and not (get_nums(cln) - t_nums):
                pts.append({"txt": cln, "cite": cites})
    if len(pts) < 3:
        seen = {c for p in pts for c in p["cite"]}
        idxs = [1, max(2, n_s // 2), n_s]
        for idx in idxs:
            if len(pts) >= 3:
                break
            if idx not in seen and 1 <= idx <= n_s:
                st = sents[idx - 1]
                cln = re.sub(r"^\d+(\.\d+)*\s*", "", st).split("(")[0].strip()
                for n in (get_nums(cln) - t_nums):
                    cln = re.sub(r"\b" + re.escape(n) + r"\b", "", cln).strip()
                if not (get_nums(cln) - t_nums) and len(cln.split()) >= 3:
                    pts.append({"txt": cln, "cite": [idx]})
                    seen.add(idx)
        i = 1
        while len(pts) < 3 and i <= n_s:
            if i not in seen:
                st = sents[i - 1]
                cln = re.sub(r"^\d+(\.\d+)*\s*", "", st).split("(")[0].strip()
                for n in (get_nums(cln) - t_nums):
                    cln = re.sub(r"\b" + re.escape(n) + r"\b", "", cln).strip()
                if not (get_nums(cln) - t_nums) and len(cln.split()) >= 3:
                    pts.append({"txt": cln, "cite": [i]})
                    seen.add(i)
            i += 1
    return pts[:5]

def fix_terms(txt, gl):
    low = txt.lower()
    known = [t for t in gl if re.search(r"\b" + re.escape(t) + r"s?\b", low)]
    out = []
    for k in known[:5]:
        out.append({"en": k, "ta": gl[k].get("ta", "")})
    return out

def fix_quiz(raw_q, sents, gl, txt):
    pts = []
    seen = set()
    n_s = len(sents)
    t_nums = get_nums(txt)
    pool = ["Kelvin", "Degree Celsius", "Fahrenheit", "Absolute zero", "Triple point", "Thermodynamic", "Equilibrium", "Refraction", "Atmosphere", "Energy"]
    if gl:
        for k, v in gl.items():
            t = v.get("en", k).capitalize()
            if t not in pool:
                pool.append(t)

    for q in raw_q:
        t = q.get("q", "").strip()
        a = q.get("a", "").strip()
        c = q.get("c", 1)
        if isinstance(c, str) and c.startswith("S"):
            c = int(c[1:])
        if not isinstance(c, int) or c < 1 or c > n_s:
            c = 1
        if not t or not a or t.lower() in seen:
            continue
        if (get_nums(t) - t_nums) or (get_nums(a) - t_nums):
            continue
        if cover(a, sents[c - 1]) < 0.6:
            for idx, s in enumerate(sents):
                if cover(a, s) >= 0.6:
                    c = idx + 1
                    break
        if cover(a, sents[c - 1]) < 0.6 or cover(a, t) > 0.8:
            continue
        opts = q.get("opts") or []
        if a not in opts:
            opts = [a]
        dist = [d for d in pool if d.lower() != a.lower() and d not in opts and a.lower() not in d.lower()]
        while len(opts) < 4 and dist:
            opts.append(dist.pop(0))
        if len(opts) >= 3 and len(set(opts)) == len(opts):
            seen.add(t.lower())
            pts.append({"q": t, "opts": opts, "ans": opts.index(a), "cite": c})

    if len(pts) < 3:
        c_used = {p["cite"] for p in pts}
        for i, s in enumerate(sents):
            if len(pts) >= 3:
                break
            cid = i + 1
            if cid in c_used:
                continue
            cand = None
            if gl:
                for t in sorted(gl.keys(), key=len, reverse=True):
                    if re.search(r"\b" + re.escape(t) + r"\b", s, re.I):
                        cand = t
                        break
            if not cand:
                ws = [w for w in re.findall(r"[a-zA-Z]+", s) if len(w) >= 6 and w.lower() not in STOPWORDS]
                if ws:
                    cand = ws[0]
            if cand:
                pat = re.compile(r"\b" + re.escape(cand) + r"\b", re.I)
                blanked = pat.sub("_____", s)
                q_t = f"Fill in the blank: {blanked}"
                if q_t.lower() in seen or (get_nums(q_t) - t_nums) or (get_nums(cand) - t_nums) or cover(cand, q_t) > 0.8:
                    continue
                dist = [d for d in pool if d.lower() != cand.lower() and cand.lower() not in d.lower()]
                opts = [cand] + dist[:3]
                if len(opts) >= 3 and len(set(opts)) == len(opts):
                    seen.add(q_t.lower())
                    c_used.add(cid)
                    pts.append({"q": q_t, "opts": opts, "ans": 0, "cite": cid})
    return pts[:4]

def fix_ex(txt):
    m, eid = pick_bank_example(txt)
    if eid:
        return {"id": eid, "txt": m}
    return {"id": EXAMPLE_BANK[0]["id"], "txt": EXAMPLE_BANK[0]["example"]}

def run_one(txt):
    res = run_pipeline(txt, be, gl)
    sents = [s[1] for s in res["s_list"]]
    h_idx = int(res["hard_s"]["id"][1:]) if res["hard_s"]["id"].startswith("S") else 1
    orig = sents[h_idx - 1]
    simp = fix_simp(orig, res["parsed"]["simple"], txt)
    summ = fix_summ(res["parsed"]["summary"].splitlines(), sents, txt)
    terms = fix_terms(txt, gl)
    quiz = fix_quiz(res["quiz"], sents, gl, txt)
    ex = fix_ex(txt)
    return {
        "sents": sents,
        "hard": h_idx,
        "simple": simp,
        "summary": summ,
        "terms": terms,
        "quiz": quiz,
        "example": ex,
    }
