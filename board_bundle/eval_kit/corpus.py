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
