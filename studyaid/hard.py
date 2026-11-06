import re
from studyaid.check import STOPWORDS, stem_w
from studyaid.gloss import find_gl

COMMON_HARD_EXCLUDE = {
    "following", "between", "through", "different", "difference",
    "together", "sentence", "another", "without", "example", "important"
}

def pick_words(txt):
    return re.findall(r'[a-zA-Z]+', txt)

def find_hard_sents(s_list):
    scored = []
    for sid, txt in s_list:
        ws = pick_words(txt)
        c_cnt = sum(1 for w in ws if len(w) >= 8)
        tot = len(ws)
        scored.append((c_cnt, tot, sid, txt))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    best = scored[0] if scored else (0, 0, "", "")
    return {"id": best[2], "text": best[3], "c_cnt": best[0], "tot": best[1]}

def extract_hard_words(txt, gl=None):
    ws = pick_words(txt)
    seen_stems = {}
    unique_ordered = []
    for w in ws:
        w_low = w.lower()
        if len(w_low) < 3 or w_low in STOPWORDS or w_low in COMMON_HARD_EXCLUDE:
            continue
        s = stem_w(w_low)
        if s not in seen_stems:
            seen_stems[s] = w_low
            unique_ordered.append(w_low)

    gl_hits = []
    other_cands = []
    for w in unique_ordered:
        hit = find_gl(w, gl) if gl else None
        if hit:
            gl_hits.append(w)
        elif len(w) >= 8:
            other_cands.append(w)
    gl_hits.sort(key=lambda x: (-len(x), x))
    other_cands.sort(key=lambda x: (-len(x), x))
    comb = gl_hits + other_cands
    return comb[:5]
