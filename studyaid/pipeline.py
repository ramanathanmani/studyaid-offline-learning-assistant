import time
import re
from studyaid.sents import split_sents
from studyaid.hard import find_hard_sents, extract_hard_words
from studyaid.readab import compare_readab
from studyaid.parse import extract_tag, parse_words, parse_quiz, validate_quiz
from studyaid.check import get_tokens, check_quiz
from studyaid.prompt import (
    build_prompt,
    build_retry_simple_prompt,
    build_retry_summary_prompt,
    build_retry_village_prompt,
    build_retry_words_prompt
)
from studyaid.gloss import find_gl

def run_pass1(backend, s_list, hard_s, cand_w, max_new=320):
    t0 = time.perf_counter()
    pmt = build_prompt(s_list, hard_s, cand_w, pass_mode=1)
    raw, tc = backend.gen(pmt, max_new=max_new)
    
    simple = extract_tag("SIMPLE", raw)
    summary = extract_tag("SUMMARY", raw)
    village = extract_tag("VILLAGE", raw)
    w_raw = extract_tag("WORDS", raw)
    
    attempts = [{"pass": 1, "attempt": 1, "tokens": tc, "sec": round(time.perf_counter() - t0, 3)}]
    reasons = []

    orig_ws = len(hard_s["text"].split())
    simp_ws = len(simple.split()) if simple else 999
    verbatim_cnt = len(set(re.findall(r'[a-zA-Z]+', simple.lower())) & set(re.findall(r'[a-zA-Z]+', hard_s["text"].lower()))) if simple else 0
    no_simpler = False
    if simp_ws >= orig_ws or verbatim_cnt >= 2 or not simple:
        t_sub = time.perf_counter()
        reasons.append("short_rewrite_guard")
        r_pmt = build_retry_simple_prompt(hard_s["text"], simple)
        r_raw, r_tc = backend.gen(r_pmt, max_new=120)
        tc += r_tc
        attempts.append({"attempt": len(attempts) + 1, "guard": "short_rewrite_guard", "tokens": r_tc, "sec": round(time.perf_counter() - t_sub, 3)})
        r_simple = extract_tag("SIMPLE", r_raw) or r_raw.strip()
        r_simp_ws = len(r_simple.split())
        if r_simp_ws < orig_ws and r_simp_ws > 0 and "no simpler" not in r_simple.lower():
            simple = r_simple
        else:
            simple = hard_s["text"]
            no_simpler = True

    summary_fallback = False
    if not summary or summary.strip().upper() == "N/A" or len(summary.split()) < 5:
        t_sub = time.perf_counter()
        reasons.append("missing_section: summary")
        s_pmt = build_retry_summary_prompt(s_list)
        s_raw, s_tc = backend.gen(s_pmt, max_new=100)
        tc += s_tc
        attempts.append({"attempt": len(attempts) + 1, "guard": "missing_summary", "tokens": s_tc, "sec": round(time.perf_counter() - t_sub, 3)})
        r_sum = extract_tag("SUMMARY", s_raw)
        if not r_sum and not any(tag in s_raw for tag in ("<SIMPLE>", "<VILLAGE>", "<WORDS>", "<QUIZ>")):
            r_sum = s_raw.strip()
        if r_sum and r_sum.strip().upper() != "N/A" and len(r_sum.split()) >= 5:
            summary = r_sum
        else:
            summary = f"{s_list[0][1]} {s_list[1][1]} (fallback: first sentences of the passage)"
            summary_fallback = True
            
    def check_vil_fmt(v_txt, sl):
        if not v_txt or not v_txt.strip():
            return False
        s_splits = [s for s in re.split(r'[.!?]+', v_txt) if len(s.strip()) > 3]
        if len(s_splits) > 3 or len(s_splits) < 1:
            return False
        v_words = set(re.findall(r'[a-zA-Z]+', v_txt.lower()))
        for _, stxt in sl:
            sw = set(re.findall(r'[a-zA-Z]+', stxt.lower()))
            if len(sw) >= 6 and len(v_words & sw) / len(sw) >= 0.85:
                return False
        return True

    vil_fmt_ok = check_vil_fmt(village, s_list)
    if not vil_fmt_ok:
        t_sub = time.perf_counter()
        reasons.append("village_format_guard")
        vr_pmt = build_retry_village_prompt(summary or hard_s["text"])
        vr_raw, vr_tc = backend.gen(vr_pmt, max_new=140)
        tc += vr_tc
        attempts.append({"attempt": len(attempts) + 1, "guard": "village_format_guard", "tokens": vr_tc, "sec": round(time.perf_counter() - t_sub, 3)})
        r_vil = extract_tag("VILLAGE", vr_raw) or vr_raw.strip()
        if r_vil and check_vil_fmt(r_vil, s_list):
            village = r_vil
            vil_fmt_ok = True
        else:
            village = r_vil or village
            vil_fmt_ok = check_vil_fmt(village, s_list)
            
    words = parse_words(w_raw, cand_words=cand_w)
    if cand_w and (not w_raw or all(w["meaning"] == "no explanation generated" for w in words)):
        t_sub = time.perf_counter()
        reasons.append("missing_section: words")
        rw_pmt = build_retry_words_prompt(cand_w)
        rw_raw, rw_tc = backend.gen(rw_pmt, max_new=120)
        tc += rw_tc
        attempts.append({"attempt": len(attempts) + 1, "guard": "missing_words", "tokens": rw_tc, "sec": round(time.perf_counter() - t_sub, 3)})
        rw_parsed = extract_tag("WORDS", rw_raw) or rw_raw.strip()
        words = parse_words(rw_parsed, cand_words=cand_w)

    retries = len(attempts) - 1
    p1_info = {
        "tokens": tc,
        "seconds": round(time.perf_counter() - t0, 3),
        "attempts": attempts,
        "retries": retries,
        "retried": retries > 0,
        "reason": "; ".join(reasons) if reasons else "none",
        "summary_fallback": summary_fallback
    }
    return simple, summary, village, words, no_simpler, vil_fmt_ok, p1_info

def run_pass2(backend, s_list, hard_s, cand_w, max_new=280):
    t0 = time.perf_counter()
    pmt = build_prompt(s_list, hard_s, cand_w, pass_mode=2)
    raw, tc = backend.gen(pmt, max_new=max_new)
    
    raw_quiz = parse_quiz(extract_tag("QUIZ", raw) or raw)
    val_quiz = validate_quiz(raw_quiz, s_list)
    
    attempts = [{"pass": 2, "attempt": 1, "valid_cnt": len(val_quiz), "tokens": tc, "sec": round(time.perf_counter() - t0, 3)}]
    reasons = []
    
    if len(val_quiz) < 3:
        t_sub = time.perf_counter()
        reasons.append(f"quiz_guard: only {len(val_quiz)}/3 valid")
        r_pmt = (
            pmt +
            "\n\nREMINDER: Each question must end with '?', have a short answer under 12 words (not copying the passage sentence), and have a different answer."
        )
        r_raw, r_tc = backend.gen(r_pmt, max_new=max_new)
        tc += r_tc
        attempts.append({"attempt": len(attempts) + 1, "guard": "quiz_guard", "tokens": r_tc, "sec": round(time.perf_counter() - t_sub, 3)})
        r_quiz = parse_quiz(extract_tag("QUIZ", r_raw) or r_raw)
        r_val = validate_quiz(r_quiz, s_list)
        if len(r_val) >= len(val_quiz):
            val_quiz = r_val
            
    retries = len(attempts) - 1
    p2_info = {
        "tokens": tc,
        "seconds": round(time.perf_counter() - t0, 3),
        "attempts": attempts,
        "retries": retries,
        "retried": retries > 0,
        "reason": "; ".join(reasons) if reasons else "none"
    }
    return val_quiz, p2_info

def run_pipeline(p_txt, backend, gl, max_new=480, max_new_p1=320, max_new_p2=280, two_pass=True):
    s_list = split_sents(p_txt)
    hard_s = find_hard_sents(s_list)
    cand_w = extract_hard_words(p_txt, gl)

    if two_pass:
        simple, summary, village, words, no_simpler, vil_fmt_ok, p1_info = run_pass1(backend, s_list, hard_s, cand_w, max_new=max_new_p1)
        val_quiz, p2_info = run_pass2(backend, s_list, hard_s, cand_w, max_new=max_new_p2)
    else:
        pmt = build_prompt(s_list, hard_s, cand_w)
        raw, tc = backend.gen(pmt, max_new=max_new)
        parsed = parse_resp(raw, cand_words=cand_w)
        simple = parsed["simple"]
        summary = parsed["summary"]
        village = parsed["village"]
        words = parsed["words"]
        val_quiz = validate_quiz(parsed["quiz"], s_list)
        no_simpler = False
        vil_fmt_ok = True
        p1_info = {"tokens": tc, "seconds": 0.0, "attempts": [], "retries": 0, "retried": False, "reason": "none", "summary_fallback": False}
        p2_info = {"tokens": 0, "seconds": 0.0, "attempts": [], "retries": 0, "retried": False, "reason": "none"}

    if no_simpler:
        readab = compare_readab(hard_s["text"], hard_s["text"])
    else:
        readab = compare_readab(hard_s["text"], simple) if simple else None
        
    w_with_gl = []
    for item in words:
        gl_match = find_gl(item["word"], gl)
        m_txt = item["meaning"]
        if gl_match and gl_match.get("verified") and gl_match.get("meaning"):
            m_txt = gl_match["meaning"]
            item["meaning"] = m_txt
        w_with_gl.append({
            "word": item["word"],
            "meaning": m_txt,
            "gl": gl_match
        })
        
    chk_quiz = check_quiz(val_quiz, s_list)
    
    model_cite_ok_cnt = sum(1 for q in chk_quiz if q.get("model_cite_correct"))
    sup_cnt = sum(1 for q in chk_quiz if "SUPPORTED" in q["status"])
    exp_cnt = sum(1 for w in words if w["meaning"] != "no explanation generated")
    
    p_res = {
        "simple": simple,
        "summary": summary,
        "village": village,
        "words": w_with_gl,
        "quiz": chk_quiz,
        "no_simpler": no_simpler,
        "valid": True
    }
    
    guards = {
        "rewrite_shorter": readab["diff"]["w_chg"] < 0 if (readab and "diff" in readab) else False,
        "no_simpler_rewrite": no_simpler,
        "summary_produced_without_fallback": not p1_info.get("summary_fallback", False),
        "village_format_ok": vil_fmt_ok,
        "village_relevant": vil_fmt_ok,
        "quiz_count": len(chk_quiz),
        "quiz_incomplete": len(chk_quiz) < 3,
        "quiz_model_cite_cnt": model_cite_ok_cnt,
        "quiz_supported_cnt": sup_cnt,
        "quiz_total_cnt": len(chk_quiz),
        "words_explained_cnt": exp_cnt,
        "words_cand_cnt": len(cand_w),
        "retries": p1_info["retries"] + p2_info["retries"],
        "p1_retried": p1_info["retried"],
        "p1_retry_reason": p1_info["reason"],
        "p2_retried": p2_info["retried"],
        "p2_retry_reason": p2_info["reason"]
    }
    
    return {
        "is_mock": getattr(backend, "is_mock", False),
        "s_list": s_list,
        "hard_s": hard_s,
        "cand_words": cand_w,
        "parsed": p_res,
        "readab": readab,
        "words": w_with_gl,
        "quiz": chk_quiz,
        "tok_cnt": p1_info["tokens"] + p2_info["tokens"],
        "p1_info": p1_info,
        "p2_info": p2_info,
        "guards": guards
    }
