import re
from studyaid.check import STOPWORDS, stem_w
from studyaid.gloss import find_gl, find_terms

COMMON_HARD_EXCLUDE = {
    "following", "between", "through", "different", "difference",
    "together", "sentence", "another", "without", "example", "important",
    "measure", "measuring", "commonly", "called"
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

def check_number_preservation(orig, simp):
    orig_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', orig))
    if not orig_nums:
        return True, []
    simp_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', simp))
    missing = orig_nums - simp_nums
    return len(missing) == 0, list(missing)

def extract_hard_words(txt, gl=None, hard_s_txt=""):
    hard_s_low = hard_s_txt.lower() if hard_s_txt else ""
    gl_terms = find_terms(txt, gl) if gl else []

    # Partition glossary terms: hardest sentence first, then rest
    in_hard_s = []
    other_gl = []
    for t in gl_terms:
        if t in COMMON_HARD_EXCLUDE:
            continue
        if hard_s_low and re.search(r"\b" + re.escape(t) + r"\b", hard_s_low):
            in_hard_s.append(t)
        else:
            other_gl.append(t)

    # Word-level candidate extraction
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

    other_cands = []
    for w in unique_ordered:
        if any(w in t for t in gl_terms):
            continue
        if len(w) >= 8:
            other_cands.append(w)

    combined = in_hard_s + other_gl + other_cands
    # Deduplicate while preserving ranking
    res = []
    for item in combined:
        if item not in res:
            res.append(item)
    return res[:5]
