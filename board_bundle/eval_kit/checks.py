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
