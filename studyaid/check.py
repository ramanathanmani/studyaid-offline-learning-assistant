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

def get_tokens(txt):
    ws = re.findall(r'[a-zA-Z]+', txt.lower())
    return {w for w in ws if len(w) > 1 and w not in STOPWORDS}

def check_item(item, s_map):
    ans_toks = get_tokens(item["a"])
    cid = item["c"].strip().upper()
    cited_txt = s_map.get(cid, "")
    cited_toks = get_tokens(cited_txt)
    sh = sorted(list(ans_toks & cited_toks))
    
    if len(sh) >= 2:
        return {
            "q": item["q"],
            "a": item["a"],
            "c": cid,
            "status": "supported",
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
        "status": "flagged",
        "shared": sh,
        "suggested": sug
    }

def check_quiz(items, s_list):
    s_map = {sid.upper(): txt for sid, txt in s_list}
    return [check_item(it, s_map) for it in items]
