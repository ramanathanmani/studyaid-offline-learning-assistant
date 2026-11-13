import re
import json
import sys
import subprocess
from pathlib import Path

def txt(pdf):
    r = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True)
    return r.stdout

def pairs(s):
    out = {}
    pat = r"^\s*([A-Za-z][A-Za-z \-]+?)\s{2,}([\u0B80-\u0BFF][\u0B80-\u0BFF \-]+)\s*$"
    for ln in s.splitlines():
        m = re.match(pat, ln)
        if m:
            out[m.group(1).strip().lower()] = m.group(2).strip()
    return out

def build(d, gl):
    for p in sorted(Path(d).glob("*.pdf")):
        pr = pairs(txt(p))
        if not pr:
            print("no pairs, check encoding or run ocr:", p.name)
        for en, ta in pr.items():
            gl.setdefault(en, {"ta": ta, "src": p.name, "ok": False})
    return gl

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python build_gl.py <books_dir> <output_glossary.json>")
        sys.exit(1)
    out = Path(sys.argv[2])
    gl = {}
    if out.exists():
        with open(out, encoding="utf-8") as f:
            gl = json.load(f)
    gl = build(sys.argv[1], gl)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(gl, f, ensure_ascii=False, indent=1)
    print(len(gl), "terms")
