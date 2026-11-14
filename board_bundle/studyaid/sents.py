import re

def split_sents(txt):
    pat = r'\b(?:e\.g\.|i\.e\.|etc\.|vs\.|al\.|mr\.|dr\.|ms\.)'
    def repl_abbr(m):
        return m.group(0).replace('.', '__DOT__')
    sub = re.sub(pat, repl_abbr, txt, flags=re.IGNORECASE)
    sub = re.sub(r'(\d)\.(\d)', lambda m: m.group(1) + '__DOT__' + m.group(2), sub)
    raw = re.split(r'(?<=[.!?])\s+', sub.strip())
    res = []
    idx = 1
    for r in raw:
        s = r.replace('__DOT__', '.').strip()
        if s:
            res.append((f"S{idx}", s))
            idx += 1
    return res
