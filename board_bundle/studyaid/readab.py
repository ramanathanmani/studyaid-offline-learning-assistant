import re

def sent_stats(txt, gl=None):
    ws = re.findall(r'[a-zA-Z0-9\.]+', txt)
    clean_words = [re.sub(r'[^a-zA-Z]', '', w).lower() for w in ws]
    clean_words = [w for w in clean_words if w]
    w_cnt = len(clean_words)
    l_cnt = sum(len(w) for w in clean_words)
    avg_l = round(l_cnt / w_cnt, 2) if w_cnt > 0 else 0.0

    sents = [s for s in re.split(r'[.!?]+', txt) if s.strip()]
    s_cnt = max(len(sents), 1)
    w_per_s = round(w_cnt / s_cnt, 2)

    def count_syllables(w):
        w = w.lower()
        if len(w) <= 3:
            return 1
        count = len(re.findall(r'[aeiouy]+', w))
        if w.endswith('e') and not w.endswith('le') and count > 1:
            count -= 1
        return max(count, 1)

    syl_cnt = sum(count_syllables(w) for w in clean_words)
    avg_syl = round(syl_cnt / w_cnt, 2) if w_cnt > 0 else 0.0

    if w_cnt > 0:
        flesch = round(206.835 - 1.015 * (w_cnt / s_cnt) - 84.6 * (syl_cnt / w_cnt), 1)
    else:
        flesch = 0.0

    gl_cnt = 0
    if gl:
        from studyaid.gloss import find_terms
        gl_cnt = len(find_terms(txt, gl))

    return {
        "w_cnt": w_cnt,
        "l_cnt": l_cnt,
        "avg_l": avg_l,
        "s_cnt": s_cnt,
        "w_per_s": w_per_s,
        "avg_syl": avg_syl,
        "flesch": flesch,
        "gl_cnt": gl_cnt
    }

def pct_diff(new_v, old_v):
    if old_v == 0:
        return 0.0
    return round(((new_v - old_v) / old_v) * 100.0, 1)

def compare_readab(orig, simp, gl=None):
    st_orig = sent_stats(orig, gl)
    st_simp = sent_stats(simp, gl)
    return {
        "orig": st_orig,
        "simp": st_simp,
        "diff": {
            "w_chg": pct_diff(st_simp["w_cnt"], st_orig["w_cnt"]),
            "l_chg": pct_diff(st_simp["l_cnt"], st_orig["l_cnt"]),
            "avg_chg": pct_diff(st_simp["avg_l"], st_orig["avg_l"]),
            "s_chg": pct_diff(st_simp["s_cnt"], st_orig["s_cnt"]),
            "w_per_s_chg": pct_diff(st_simp["w_per_s"], st_orig["w_per_s"]),
            "syl_chg": pct_diff(st_simp["avg_syl"], st_orig["avg_syl"]),
            "flesch_diff": round(st_simp["flesch"] - st_orig["flesch"], 1),
            "gl_chg": pct_diff(st_simp["gl_cnt"], st_orig["gl_cnt"]) if st_orig["gl_cnt"] > 0 else 0.0
        }
    }
