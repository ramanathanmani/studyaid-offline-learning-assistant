import re

def sent_stats(txt):
    ws = re.findall(r'[a-zA-Z]+', txt)
    w_cnt = len(ws)
    l_cnt = sum(len(w) for w in ws)
    avg_l = round(l_cnt / w_cnt, 2) if w_cnt > 0 else 0.0
    return {"w_cnt": w_cnt, "l_cnt": l_cnt, "avg_l": avg_l}

def pct_diff(new_v, old_v):
    if old_v == 0:
        return 0.0
    return round(((new_v - old_v) / old_v) * 100.0, 1)

def compare_readab(orig, simp):
    st_orig = sent_stats(orig)
    st_simp = sent_stats(simp)
    return {
        "orig": st_orig,
        "simp": st_simp,
        "diff": {
            "w_chg": pct_diff(st_simp["w_cnt"], st_orig["w_cnt"]),
            "l_chg": pct_diff(st_simp["l_cnt"], st_orig["l_cnt"]),
            "avg_chg": pct_diff(st_simp["avg_l"], st_orig["avg_l"])
        }
    }
