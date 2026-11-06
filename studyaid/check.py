import re

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "being",
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

COMMON_SCHOOL_WORDS = {
    "what", "why", "how", "which", "called", "known", "process", "result",
    "form", "forms", "take", "takes", "place", "occur", "occurs", "difference",
    "type", "types", "example", "examples", "different", "following", "point",
    "state", "change", "changes", "body", "food", "substance", "substances",
    "part", "parts", "complex", "simple", "simpl", "passage", "sentence",
    "following", "main", "primary", "function"
}

def stem_w(w):
    w = w.lower().strip()
    if len(w) <= 3:
        return w
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("ly") and len(w) > 4:
        w = w[:-2]
    if w.endswith("tion") and len(w) > 5:
        w = w[:-3]
    elif w.endswith("sion") and len(w) > 5:
        w = w[:-3]
    elif w.endswith("ing") and len(w) > 5:
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

def score_sentences(q_txt, a_txt, s_list):
    a_toks = get_tokens(a_txt)
    q_toks = get_tokens(q_txt)
    comb_toks = a_toks | q_toks
    if not comb_toks:
        return None, []

    n_sents = len(s_list)
    df = {}
    s_tok_map = {}
    for sid, txt in s_list:
        st = get_tokens(txt)
        s_tok_map[sid] = st
        for w in st:
            df[w] = df.get(w, 0) + 1

    distinctive = set()
    for w in comb_toks:
        if w in COMMON_SCHOOL_WORDS or w in STOPWORDS:
            continue
        d_cnt = df.get(w, 0)
        if 1 <= d_cnt <= max(1, n_sents // 2):
            distinctive.add(w)

    best_sid = None
    best_score = -1.0
    best_shared = []

    for sid, txt in s_list:
        st = s_tok_map[sid]
        match_distinctive = distinctive & st
        if not match_distinctive and len(a_toks) > 1:
            continue
        if len(a_toks) == 1:
            single_w = list(a_toks)[0]
            if single_w not in st:
                continue

        score = 0.0
        sh_a = a_toks & st
        sh_q = q_toks & st
        for w in sh_a:
            w_df = df.get(w, 1)
            base_w = 0.05 if w in COMMON_SCHOOL_WORDS else (1.0 / w_df)
            score += base_w * 3.0
        for w in sh_q:
            w_df = df.get(w, 1)
            base_w = 0.05 if w in COMMON_SCHOOL_WORDS else (1.0 / w_df)
            score += base_w * 1.0

        if score > best_score:
            best_score = score
            best_sid = sid
            best_shared = sorted(list(sh_a))

    if best_score <= 0.1:
        return None, []
    return best_sid, best_shared

def check_item(item, s_list):
    s_map = {sid.upper(): txt for sid, txt in s_list}
    raw_cid = item.get("c", "").strip().upper()
    best_sid, shared_words = score_sentences(item["q"], item["a"], s_list)

    ans_toks = get_tokens(item["a"])
    is_single = len(ans_toks) == 1

    if best_sid is not None:
        model_ok = (raw_cid == best_sid)
        status = "SUPPORTED (exact term)" if is_single else "SUPPORTED"
        suggested = None if model_ok else best_sid
        return {
            "q": item["q"],
            "a": item["a"],
            "model_cite": raw_cid,
            "c": best_sid,
            "status": status,
            "model_cite_correct": model_ok,
            "auto_corrected": (not model_ok and raw_cid != ""),
            "shared": shared_words,
            "suggested": suggested
        }

    return {
        "q": item["q"],
        "a": item["a"],
        "model_cite": raw_cid,
        "c": raw_cid,
        "status": "FLAGGED",
        "model_cite_correct": False,
        "auto_corrected": False,
        "shared": [],
        "suggested": None
    }

def check_quiz(items, s_list):
    return [check_item(it, s_list) for it in items]
