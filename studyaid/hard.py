import re

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

def extract_hard_words(txt):
    ws = pick_words(txt)
    cand = sorted(list({w.lower() for w in ws if len(w) >= 8}))
    return cand
