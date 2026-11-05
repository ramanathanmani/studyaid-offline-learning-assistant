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
    for item in data:
        k = item['en'].strip().lower()
        gl[k] = {
            'en': item['en'],
            'ta': item['ta'],
            'translit': item['translit'],
            'verified': item.get('verified', False),
            'source': item.get('source', '')
        }
    return gl

def find_gl(w, gl):
    for c in norm_cand(w):
        if c in gl:
            return gl[c]
    return None
