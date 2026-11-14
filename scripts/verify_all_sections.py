import sys, os, json, re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "eval_kit"))
sys.path.insert(0, str(root))

from checks import score_one, total, cover, nums, toks, nsents, W

def verify_all_sections(gw_result_path, text_path, gl_path, bank_path):
    print("=" * 70)
    print("        STUDYAID HACKATHON OUTPUT VERIFIER - ALL SECTIONS")
    print("=" * 70)

    with open(gw_result_path, encoding="utf-8") as f:
        out = json.load(f)

    with open(text_path, encoding="utf-8") as f:
        txt = f.read().strip()

    with open(gl_path, encoding="utf-8") as f:
        gl = json.load(f)

    with open(bank_path, encoding="utf-8") as f:
        bank = set(json.load(f))

    rec = {"ok": True, "out": out}
    row = {"text": txt, "ta_book": None}

    s = score_one(rec, row, gl, bank, "")
    tot_score = total(s)

    sents = out.get("sents", [])
    print(f"\n[SECTION 1: SENTENCE SEGMENTATION]")
    print(f"  • Total sentences parsed: {len(sents)}")
    assert len(sents) >= 20, f"Expected at least 20 sentences, got {len(sents)}"
    print(f"  ✓ PASS: Sentence segmentation valid (S1 - S{len(sents)})")

    print(f"\n[SECTION 2: HARDEST SENTENCE & SIMPLIFICATION]")
    hard_idx = out.get("hard")
    orig_hard = sents[hard_idx - 1] if 0 < hard_idx <= len(sents) else ""
    simple = out.get("simple", "")
    print(f"  • Hardest sentence index: S{hard_idx}")
    print(f"  • Original complex text : \"{orig_hard}\"")
    print(f"  • Simplified plain text : \"{simple}\"")
    
    orig_nums = nums(orig_hard)
    simp_nums = nums(simple)
    txt_nums = nums(txt)
    num_ok = orig_nums <= simp_nums and not (simp_nums - txt_nums)
    c_val = cover(orig_hard, simple)
    w_orig = len(orig_hard.split())
    w_simp = len(simple.split()) / nsents(simple)
    
    print(f"  • Numbers preserved    : {orig_nums <= simp_nums} (orig: {orig_nums}, simp: {simp_nums})")
    print(f"  • Token coverage       : {c_val:.2%} (required >= 50%)")
    print(f"  • Words per sentence   : {w_simp:.1f} vs orig {w_orig}")
    print(f"  • Simplified != Orig   : {simple != orig_hard}")
    assert s["simp"], "Simplification check failed in official scoring"
    print(f"  ✓ PASS: Sentence simplification verified ({W['simp']} / {W['simp']} pts)")

    print(f"\n[SECTION 3: SUMMARY POINTS WITH SOURCE CITATIONS]")
    summary = out.get("summary", [])
    print(f"  • Total summary points : {len(summary)}")
    assert len(summary) >= 3, "Summary must have at least 3 points"
    for i, pt in enumerate(summary, 1):
        pt_txt = pt.get("txt", "")
        cites = pt.get("cite", [])
        src = " ".join(sents[c - 1] for c in cites if 0 < c <= len(sents))
        c_cov = cover(pt_txt, src)
        cite_str = ", ".join(f"S{c}" for c in cites)
        print(f"    [{i}] \"{pt_txt}\" [{cite_str}] (coverage: {c_cov:.2%})")
        assert c_cov >= 0.4, f"Summary point {i} coverage {c_cov:.2%} < 40%"
    assert s["summ"], "Summary check failed in official scoring"
    print(f"  ✓ PASS: Summary points with citations verified ({W['summ']} / {W['summ']} pts)")

    print(f"\n[SECTION 4: BILINGUAL GLOSSARY & TAMIL DEFINITIONS]")
    terms = out.get("terms", [])
    print(f"  • Total glossary terms : {len(terms)}")
    assert len(terms) >= 5, "Glossary must have at least 5 terms"
    for i, t in enumerate(terms, 1):
        en = t.get("en", "")
        ta = t.get("ta", "")
        defin = t.get("def", "")
        in_txt = bool(re.search(r"\b" + re.escape(en) + r"s?\b", txt, re.I))
        in_gl = en in gl
        print(f"    [{i}] {en.ljust(18)} -> {ta.ljust(22)} | in_txt: {in_txt} | has_def: {bool(defin)}")
        assert in_txt, f"Term {en} not in passage text!"
        assert in_gl, f"Term {en} not in glossary!"
        assert defin, f"Term {en} missing definition!"
    assert s["gloss"], "Glossary check failed in official scoring"
    print(f"  ✓ PASS: Bilingual glossary and definitions verified ({W['gloss']} / {W['gloss']} pts)")

    print(f"\n[SECTION 5: EVERYDAY RURAL VILLAGE ANALOGY]")
    ex = out.get("example", {})
    ex_id = ex.get("id", "")
    ex_en = ex.get("en", "")
    ex_ta = ex.get("ta", "")
    print(f"  • Example ID   : {ex_id}")
    print(f"  • English story: \"{ex_en}\"")
    print(f"  • Tamil story  : \"{ex_ta}\"")
    assert ex_id in bank, f"Example ID {ex_id} not in approved bank!"
    assert len(ex_en) > 30 and len(ex_ta) > 30, "Example text too short"
    assert s["exam"], "Example check failed in official scoring"
    print(f"  ✓ PASS: Relatable village example verified ({W['exam']} / {W['exam']} pts)")

    print(f"\n[SECTION 6: INTERACTIVE QUIZ & ANSWER CITATIONS]")
    quiz = out.get("quiz", [])
    print(f"  • Total quiz questions: {len(quiz)}")
    assert len(quiz) >= 3, "Quiz must have at least 3 questions"
    for i, q in enumerate(quiz, 1):
        q_txt = q.get("q", "")
        opts = q.get("opts", [])
        ans_idx = q.get("ans", 0)
        ans_txt = opts[ans_idx] if 0 <= ans_idx < len(opts) else ""
        cite = q.get("cite", 1)
        src_sent = sents[cite - 1] if 0 < cite <= len(sents) else ""
        a_cov = cover(ans_txt, src_sent)
        print(f"    Q{i}: \"{q_txt}\"")
        print(f"        Options : {opts}")
        print(f"        Answer  : [{chr(65+ans_idx)}] \"{ans_txt}\" (cited S{cite}, coverage: {a_cov:.2%})")
        assert len(opts) == 4, f"Q{i} must have 4 options"
        assert len(set(opts)) == 4, f"Q{i} options must be unique"
        assert a_cov >= 0.6, f"Q{i} answer coverage {a_cov:.2%} < 60%"
    assert s["quiz"], "Quiz check failed in official scoring"
    print(f"  ✓ PASS: Interactive quiz with citations verified ({W['quiz']} / {W['quiz']} pts)")

    print(f"\n[SECTION 7: NUMERICAL INTEGRITY & FORMAT]")
    assert s["nums"], "Numerical integrity failed"
    assert s["fmt"], "Format/UTF-8 integrity failed"
    print(f"  • No hallucinated numbers: PASS")
    print(f"  • Clean UTF-8 encoding   : PASS ({W['fmt']} / {W['fmt']} pts)")

    print("\n" + "=" * 70)
    print(f"       OFFICIAL EVALUATION SCORE: {tot_score} / 100")
    print("=" * 70)
    print(f"  Score Breakdown:")
    for k in W:
        mark = "✓" if s[k] else "✗"
        print(f"    {mark} {k.ljust(8)}: {W[k] if s[k] else 0} / {W[k]} pts")
    print("=" * 70)
    return tot_score == 100

if __name__ == "__main__":
    gw_res = sys.argv[1] if len(sys.argv) > 1 else "/home/rock/studyaid/final/gw_result.json"
    txt_f = sys.argv[2] if len(sys.argv) > 2 else "/home/rock/Downloads/Problem Statement Dataset/PS1/Global warming is one of the most s.txt"
    gl_f = sys.argv[3] if len(sys.argv) > 3 else "/home/rock/studyaid/final/glossary.json"
    bank_f = sys.argv[4] if len(sys.argv) > 4 else "/home/rock/studyaid/eval_kit/example_bank.json"
    
    ok = verify_all_sections(gw_res, txt_f, gl_f, bank_f)
    sys.exit(0 if ok else 1)
