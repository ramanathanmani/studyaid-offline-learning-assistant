import re
from studyaid.check import is_ans_too_long_or_copied

def extract_tag(tag, txt):
    if not txt:
        return None
    t_clean = tag.strip().upper()
    if t_clean == "VILLAGE":
        t_pat = r'(?:S)?(?:VILLAGE|SVILLE|VILLE)'
    else:
        t_pat = rf'(?:S)?{t_clean}'
    m = re.search(rf'<{t_pat}[^>]*>(.*?)</{t_pat}>', txt, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    known = ["SIMPLE", "SUMMARY", "VILLAGE", "SVILLE", "WORDS", "QUIZ"]
    others = [k for k in known if not k.startswith(t_clean[:3])]
    other_pat = "|".join(others)
    pat = rf'<{t_pat}[^>]*>(.*?)(?=(?:<(?:S)?(?:{other_pat})[^>]*>)|\Z)'
    m2 = re.search(pat, txt, re.DOTALL | re.IGNORECASE)
    if m2:
        res = m2.group(1).strip()
        res = re.sub(rf'</{t_pat}>$', '', res, flags=re.IGNORECASE).strip()
        return res if res else None
    return None

def parse_words(txt, cand_words=None):
    if not txt:
        if cand_words:
            return [{"word": cw, "meaning": "no explanation generated"} for cw in cand_words]
        return []
    cand_set = {c.strip().lower() for c in (cand_words or [])}
    parsed = {}
    for line in txt.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2:
                w = parts[0].strip().lower()
                m = parts[1].strip()
                if cand_set and w in cand_set:
                    parsed[w] = m
                elif not cand_set:
                    parsed[w] = m
        elif ':' in line:
            parts = [p.strip() for p in line.split(':', 1)]
            if len(parts) >= 2:
                w = parts[0].strip().lower()
                m = parts[1].strip()
                if cand_set and w in cand_set:
                    parsed[w] = m
                elif not cand_set:
                    parsed[w] = m

    res = []
    if cand_words:
        for cw in cand_words:
            c_low = cw.strip().lower()
            m = parsed.get(c_low)
            if not m or m.lower() in ["simple", "meaning", "one line each"]:
                m = "no explanation generated"
            res.append({"word": cw, "meaning": m})
    else:
        for w, m in parsed.items():
            res.append({"word": w, "meaning": m or "no explanation generated"})
    return res

def parse_quiz(txt):
    if not txt:
        return []
    items = []
    pat = r'Q:\s*(.*?)\s*\nA:\s*(.*?)(?:\s*\nC:\s*(.*?))?(?=\nQ:|\Z)'
    matches = re.findall(pat, txt.strip() + '\n', re.DOTALL | re.IGNORECASE)
    for q, a, c in matches:
        cid_match = re.search(r'S\d+', c or a, re.IGNORECASE)
        cid = cid_match.group(0).upper() if cid_match else "S1"
        clean_a = re.sub(r'\(?\s*S\d+\s*\)?', '', a).strip()
        items.append({
            "q": q.strip(),
            "a": clean_a or a.strip(),
            "c": cid
        })
    return items

def validate_quiz(items, s_list):
    valid = []
    seen_ans = set()
    s_map = {sid.upper(): txt for sid, txt in s_list}
    s_word_sets = [set(re.findall(r'[a-zA-Z]+', txt.lower())) for _, txt in s_list]
    for it in items:
        q = it["q"].strip()
        a = it["a"].strip()
        cid = it.get("c", "").strip().upper()
        if not q.endswith("?"):
            continue
        if not a:
            continue
        if re.match(r'^\[?S\d+\]?$', a.strip(), re.IGNORECASE):
            continue
        ans_norm = a.lower()
        if ans_norm in seen_ans:
            continue
        c_txt = s_map.get(cid, "")
        if c_txt and is_ans_too_long_or_copied(a, c_txt):
            continue
        q_words = set(re.findall(r'[a-zA-Z]+', q.lower()))
        if not q_words:
            continue
        is_copied = False
        for s_words in s_word_sets:
            ov = len(q_words & s_words) / len(q_words)
            if len(q_words) >= 8 and ov >= 0.8:
                is_copied = True
                break
        if is_copied:
            continue
        seen_ans.add(ans_norm)
        valid.append(it)
    return valid

def parse_resp(raw, cand_words=None):
    simple = extract_tag("SIMPLE", raw)
    summary = extract_tag("SUMMARY", raw)
    village = extract_tag("VILLAGE", raw)
    words_raw = extract_tag("WORDS", raw)
    quiz_raw = extract_tag("QUIZ", raw)
    if not quiz_raw and "<QUIZ>" in raw:
        quiz_raw = raw.split("<QUIZ>", 1)[1].split("</QUIZ>")[0]
    
    words = parse_words(words_raw, cand_words) if words_raw else []
    quiz = parse_quiz(quiz_raw) if quiz_raw else []
    
    missing = []
    if not simple:
        missing.append("SIMPLE")
    if not summary:
        missing.append("SUMMARY")
    if not village:
        missing.append("VILLAGE")
    if not words_raw or not words:
        missing.append("WORDS")
    if not quiz_raw or len(quiz) < 3:
        missing.append("QUIZ")
        
    return {
        "simple": simple or "",
        "summary": summary or "",
        "village": village or "",
        "words": words,
        "quiz": quiz,
        "missing": missing,
        "valid": len(missing) == 0
    }
