import re

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "did",
    "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further",
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself",
    "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "she", "should", "so", "some", "such", "than", "that",
    "the", "their", "theirs", "them", "themselves", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while",
    "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself"
}

def stem_w(w):
    w = w.lower().strip()
    if len(w) <= 3:
        return w
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("ly") and len(w) > 4:
        w = w[:-2]
    if w.endswith("ing") and len(w) > 5:
        w = w[:-3]
    elif w.endswith("ed") and len(w) > 4:
        w = w[:-2]
    elif w.endswith("es") and len(w) > 4:
        w = w[:-2]
    elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]
    if w.endswith("e") and len(w) > 4:
        w = w[:-1]
    return w

def get_tokens(txt):
    ws = re.findall(r'[a-zA-Z]+', txt.lower())
    return {stem_w(w) for w in ws if len(w) > 1 and w not in STOPWORDS}

def is_ans_too_long_or_copied(a_txt, c_txt):
    ws_a = re.findall(r'[a-zA-Z]+', a_txt.lower())
    if len(ws_a) > 12:
        return True
    ws_c = re.findall(r'[a-zA-Z]+', c_txt.lower())
    if not ws_c or len(ws_c) < 5:
        return False
    a_set = {stem_w(w) for w in ws_a}
    c_set = {stem_w(w) for w in ws_c}
    ov = len(a_set & c_set) / max(len(c_set), 1)
    if ov >= 0.90:
        return True
    clean_a = re.sub(r'[^a-z0-9]', '', a_txt.lower())
    clean_c = re.sub(r'[^a-z0-9]', '', c_txt.lower())
    if clean_c and clean_c in clean_a:
        return True
    return False

def check_item(item, s_map):
    ans_toks = get_tokens(item["a"])
    cid = item["c"].strip().upper()
    cited_txt = s_map.get(cid, "")
    cited_toks = get_tokens(cited_txt)
    sh = sorted(list(ans_toks & cited_toks))
    
    if len(ans_toks) == 1:
        w = list(ans_toks)[0]
        if w in cited_toks:
            return {
                "q": item["q"],
                "a": item["a"],
                "c": cid,
                "status": "SUPPORTED (exact term)",
                "shared": sh,
                "suggested": None
            }
        best_sid = None
        for sid, txt in s_map.items():
            if sid == cid:
                continue
            if w in get_tokens(txt):
                best_sid = sid
                break
        return {
            "q": item["q"],
            "a": item["a"],
            "c": cid,
            "status": "FLAGGED",
            "shared": sh,
            "suggested": best_sid
        }
    
    if len(sh) >= 2:
        return {
            "q": item["q"],
            "a": item["a"],
            "c": cid,
            "status": "SUPPORTED",
            "shared": sh,
            "suggested": None
        }
    
    best_sid = None
    best_cnt = 0
    for sid, txt in s_map.items():
        if sid == cid:
            continue
        stoks = get_tokens(txt)
        ov = len(ans_toks & stoks)
        if ov > best_cnt:
            best_cnt = ov
            best_sid = sid
            
    sug = best_sid if best_cnt >= 2 else None
    return {
        "q": item["q"],
        "a": item["a"],
        "c": cid,
        "status": "FLAGGED",
        "shared": sh,
        "suggested": sug
    }

def check_quiz(items, s_list):
    s_map = {sid.upper(): txt for sid, txt in s_list}
    return [check_item(it, s_map) for it in items]
