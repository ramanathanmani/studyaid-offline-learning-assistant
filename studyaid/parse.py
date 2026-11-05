import re

def extract_tag(tag, txt):
    m = re.search(rf'<(?:S)?{tag}>(.*?)</(?:S)?{tag}>', txt, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None

def parse_words(txt):
    if not txt:
        return []
    res = []
    for line in txt.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if '|' in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) > 2 and all(len(p.split()) <= 3 for p in parts):
                for p in parts:
                    if p.lower() not in ["simple", "meaning", "one line each"]:
                        res.append({"word": p, "meaning": "key textbook term"})
            elif len(parts) >= 2:
                res.append({"word": parts[0], "meaning": parts[1]})
            elif len(parts) == 1:
                res.append({"word": parts[0], "meaning": "key textbook term"})
        elif ':' in line:
            parts = line.split(':', 1)
            w = parts[0].strip()
            m = parts[1].strip()
            if w and m:
                res.append({"word": w, "meaning": m})
        elif line:
            res.append({"word": line.strip("-*• "), "meaning": "key textbook term"})
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

def parse_resp(raw):
    simple = extract_tag("SIMPLE", raw)
    summary = extract_tag("SUMMARY", raw)
    village = extract_tag("VILLAGE", raw)
    words_raw = extract_tag("WORDS", raw)
    quiz_raw = extract_tag("QUIZ", raw)
    if not quiz_raw and "<QUIZ>" in raw:
        quiz_raw = raw.split("<QUIZ>", 1)[1].split("</QUIZ>")[0]
    
    words = parse_words(words_raw) if words_raw else []
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
