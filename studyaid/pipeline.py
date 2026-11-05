import time
import re
from studyaid.sents import split_sents
from studyaid.hard import find_hard_sents, extract_hard_words
from studyaid.prompt import (
    build_prompt,
    build_retry_simple_prompt,
    build_retry_village_prompt
)
from studyaid.parse import parse_words, parse_quiz, validate_quiz, extract_tag
from studyaid.readab import compare_readab
from studyaid.check import check_quiz, get_tokens
from studyaid.gloss import find_gl

def run_pass1(backend, s_list, hard_s, cand_w, max_new=320):
    t0 = time.perf_counter()
    pmt = build_prompt(s_list, hard_s, cand_w, pass_mode=1)
    raw, tc = backend.gen(pmt, max_new=max_new)
    sec = time.perf_counter() - t0
    
    simple = extract_tag("SIMPLE", raw) or ""
    summary = extract_tag("SUMMARY", raw) or ""
    village = extract_tag("VILLAGE", raw) or ""
    w_raw = extract_tag("WORDS", raw) or ""
    
    p1_retried = False
    p1_reason = []
    
    orig_ws = len(hard_s["text"].split())
    simp_ws = len(simple.split()) if simple else 0
    other_s = [txt.strip().lower() for sid, txt in s_list if sid != hard_s["id"]]
    verbatim_cnt = sum(1 for ost in other_s if ost in simple.lower()) if simple else 0
    
    no_simpler = False
    if simp_ws >= orig_ws or verbatim_cnt >= 2 or not simple:
        p1_retried = True
        p1_reason.append("simplification guard")
        r_pmt = build_retry_simple_prompt(hard_s["text"], simple)
        r_raw, r_tc = backend.gen(r_pmt, max_new=120)
        tc += r_tc
        r_simple = extract_tag("SIMPLE", r_raw) or r_raw.strip()
        r_simp_ws = len(r_simple.split())
        if r_simp_ws < orig_ws and r_simp_ws > 0 and "no simpler" not in r_simple.lower():
            simple = r_simple
        else:
            simple = hard_s["text"]
            no_simpler = True
            
    key_toks = get_tokens(hard_s["text"])
    vil_toks = get_tokens(village)
    vil_rel = True
    if len(vil_toks & key_toks) < 2:
        p1_retried = True
        p1_reason.append("village relevance guard")
        vr_pmt = build_retry_village_prompt(hard_s["text"])
        vr_raw, vr_tc = backend.gen(vr_pmt, max_new=180)
        tc += vr_tc
        r_vil = extract_tag("VILLAGE", vr_raw) or vr_raw.strip()
        if len(get_tokens(r_vil) & key_toks) >= 2:
            village = r_vil
            vil_rel = True
        else:
            village = (r_vil or village) + " (low relevance to passage)"
            vil_rel = False
            
    words = parse_words(w_raw, cand_words=cand_w)
    
    p1_info = {
        "tokens": tc,
        "seconds": round(time.perf_counter() - t0, 3),
        "retried": p1_retried,
        "reason": "; ".join(p1_reason) if p1_reason else "none"
    }
    return simple, summary, village, words, no_simpler, vil_rel, p1_info

def run_pass2(backend, s_list, hard_s, cand_w, max_new=220):
    t0 = time.perf_counter()
    pmt = build_prompt(s_list, hard_s, cand_w, pass_mode=2)
    raw, tc = backend.gen(pmt, max_new=max_new)
    
    raw_quiz = parse_quiz(extract_tag("QUIZ", raw) or raw)
    val_quiz = validate_quiz(raw_quiz, s_list)
    
    p2_retried = False
    p2_reason = "none"
    if len(val_quiz) < 3:
        p2_retried = True
        p2_reason = f"quiz guards: only {len(val_quiz)}/3 valid"
        r_pmt = pmt + "\n\nEach question must end with '?', have a distinct answer, and not copy passage sentences."
        r_raw, r_tc = backend.gen(r_pmt, max_new=max_new)
        tc += r_tc
        r_quiz = parse_quiz(extract_tag("QUIZ", r_raw) or r_raw)
        r_val = validate_quiz(r_quiz, s_list)
        if len(r_val) >= len(val_quiz):
            val_quiz = r_val
            
    p2_info = {
        "tokens": tc,
        "seconds": round(time.perf_counter() - t0, 3),
        "retried": p2_retried,
        "reason": p2_reason
    }
    return val_quiz, p2_info

def run_pipeline(p_txt, backend, gl, max_new=480, max_new_p1=320, max_new_p2=220, two_pass=True):
    s_list = split_sents(p_txt)
    hard_s = find_hard_sents(s_list)
    cand_w = extract_hard_words(p_txt, gl)
    
    p1_max = max_new_p1 if two_pass else max_new
    p2_max = max_new_p2 if two_pass else max_new
    
    simple, summary, village, words, no_simpler, vil_rel, p1_info = run_pass1(
        backend, s_list, hard_s, cand_w, max_new=p1_max
    )
    val_quiz, p2_info = run_pass2(
        backend, s_list, hard_s, cand_w, max_new=p2_max
    )
    
    tot_tok = p1_info["tokens"] + p2_info["tokens"]
    
    if no_simpler:
        readab = compare_readab(hard_s["text"], hard_s["text"])
    else:
        readab = compare_readab(hard_s["text"], simple) if simple else None
        
    w_with_gl = []
    for item in words:
        gl_match = find_gl(item["word"], gl)
        w_with_gl.append({
            "word": item["word"],
            "meaning": item["meaning"],
            "gl": gl_match
        })
        
    chk_quiz = check_quiz(val_quiz, s_list)
    
    sup_cnt = sum(1 for q in chk_quiz if "SUPPORTED" in q["status"])
    exp_cnt = sum(1 for w in words if w["meaning"] != "no explanation generated")
    
    p_res = {
        "simple": simple,
        "summary": summary,
        "village": village,
        "words": words,
        "quiz": val_quiz,
        "no_simpler": no_simpler,
        "valid": True
    }
    
    guards = {
        "rewrite_shorter": (not no_simpler) and (len(simple.split()) < len(hard_s["text"].split())),
        "no_simpler_rewrite": no_simpler,
        "village_relevant": vil_rel,
        "quiz_supported_cnt": sup_cnt,
        "quiz_total_cnt": len(chk_quiz),
        "words_explained_cnt": exp_cnt,
        "words_cand_cnt": len(cand_w),
        "p1_retried": p1_info["retried"],
        "p1_retry_reason": p1_info["reason"],
        "p2_retried": p2_info["retried"],
        "p2_retry_reason": p2_info["reason"]
    }
    
    return {
        "s_list": s_list,
        "hard_s": hard_s,
        "cand_words": cand_w,
        "parsed": p_res,
        "readab": readab,
        "words": w_with_gl,
        "quiz": chk_quiz,
        "tok_cnt": tot_tok,
        "p1_info": p1_info,
        "p2_info": p2_info,
        "guards": guards,
        "is_mock": getattr(backend, "is_mock", False)
    }
