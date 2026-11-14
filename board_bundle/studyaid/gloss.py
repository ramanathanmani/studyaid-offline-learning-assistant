import json
import re

def norm_cand(w):
    w = re.sub(r'[^a-zA-Z]', '', w).lower()
    if not w:
        return []
    cands = [w]
    if w.endswith('ing') and len(w) > 4:
        cands.append(w[:-3])
        cands.append(w[:-3] + 'e')
    if w.endswith('es') and len(w) > 3:
        cands.append(w[:-2])
    if w.endswith('s') and len(w) > 2 and not w.endswith('ss'):
        cands.append(w[:-1])
    if w.endswith('ed') and len(w) > 3:
        cands.append(w[:-2])
        cands.append(w[:-1])
    if w.endswith('ly') and len(w) > 3:
        cands.append(w[:-2])
    seen = []
    for c in cands:
        if c not in seen:
            seen.append(c)
    return seen

def load_gl(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    gl = {}
    if isinstance(data, list):
        for item in data:
            k = item.get('en', '').strip().lower()
            if not k:
                continue
            en_meaning = item.get('meaning') or item.get('en_def', '')
            gl[k] = {
                'en': item.get('en', k),
                'ta': item.get('ta', ''),
                'translit': item.get('translit', ''),
                'meaning': en_meaning,
                'en_def': en_meaning,
                'ta_def': item.get('ta_def', ''),
                'sub': item.get('sub', 'science'),
                'ok': item.get('ok', item.get('verified', False)),
                'verified': item.get('verified', item.get('ok', False)),
                'source': item.get('source', '') or item.get('src', ''),
                'ref': item.get('ref', '')
            }
    elif isinstance(data, dict):
        for k, item in data.items():
            k_low = k.strip().lower()
            en_meaning = item.get('en_def') or item.get('meaning', '')
            gl[k_low] = {
                'en': item.get('en', k),
                'ta': item.get('ta', ''),
                'translit': item.get('translit', ''),
                'meaning': en_meaning,
                'en_def': en_meaning,
                'ta_def': item.get('ta_def', ''),
                'sub': item.get('sub', 'science'),
                'ok': item.get('ok', item.get('verified', False)),
                'verified': item.get('verified', item.get('ok', False)),
                'source': item.get('src', '') or item.get('source', ''),
                'ref': item.get('ref', '')
            }
    return gl

def find_terms(txt, gl):
    low = txt.lower()
    hits = []
    for t in sorted(gl.keys(), key=len, reverse=True):
        pattern = r"\b" + re.escape(t) + r"(?:s|es|ing)?\b"
        if re.search(pattern, low):
            hits.append(t)
            low = re.sub(pattern, " ", low)
    return hits

def find_gl(w, gl):
    if not gl or not w:
        return None
    w_low = w.lower().strip()
    if w_low in gl:
        return gl[w_low]
    for c in norm_cand(w_low):
        if c in gl:
            return gl[c]
    for k, v in gl.items():
        if k.startswith(w_low) and len(w_low) >= 6:
            return v
        if w_low.startswith(k) and len(k) >= 5:
            return v
        if k == 'medium' and w_low == 'media':
            return v
    return None
