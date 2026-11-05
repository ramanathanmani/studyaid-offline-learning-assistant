from studyaid.sents import split_sents
from studyaid.hard import find_hard_sents, extract_hard_words
from studyaid.prompt import build_prompt
from studyaid.parse import parse_resp, parse_quiz, extract_tag
from studyaid.readab import compare_readab
from studyaid.check import check_quiz
from studyaid.gloss import find_gl

def run_pipeline(p_txt, backend, gl, max_new=480, two_pass=False):
    s_list = split_sents(p_txt)
    hard_s = find_hard_sents(s_list)
    cand_w = extract_hard_words(p_txt)
    tok_cnt = 0

    if not two_pass:
        pmt = build_prompt(s_list, hard_s, cand_w)
        raw, tc = backend.gen(pmt, max_new=max_new)
        tok_cnt += tc
        p_res = parse_resp(raw)
        if not p_res["valid"]:
            r_pmt = pmt + "\n\nEnsure all tags are complete: SIMPLE, SUMMARY, VILLAGE, WORDS, QUIZ."
            raw2, tc2 = backend.gen(r_pmt, max_new=max_new)
            tok_cnt += tc2
            p_res2 = parse_resp(raw2)
            for k in ["simple", "summary", "village"]:
                if not p_res[k] and p_res2[k]:
                    p_res[k] = p_res2[k]
            if not p_res["words"] and p_res2["words"]:
                p_res["words"] = p_res2["words"]
            if len(p_res["quiz"]) < 3 and len(p_res2["quiz"]) >= 3:
                p_res["quiz"] = p_res2["quiz"]
            p_res["missing"] = [k for k in ["SIMPLE", "SUMMARY", "VILLAGE", "WORDS"] if not p_res[k.lower()]]
            if len(p_res["quiz"]) < 3:
                p_res["missing"].append("QUIZ")
            p_res["valid"] = len(p_res["missing"]) == 0
    else:
        p1 = build_prompt(s_list, hard_s, cand_w, pass_mode=1)
        raw1, tc1 = backend.gen(p1, max_new=max_new)
        tok_cnt += tc1
        p2 = build_prompt(s_list, hard_s, cand_w, pass_mode=2)
        raw2, tc2 = backend.gen(p2, max_new=max_new)
        tok_cnt += tc2
        comb = raw1 + "\n" + raw2
        p_res = parse_resp(comb)
        if not p_res["valid"]:
            if "QUIZ" in p_res["missing"]:
                r_raw2, r_tc2 = backend.gen(p2 + "\n\nProvide at least 3 quiz questions.", max_new=max_new)
                tok_cnt += r_tc2
                qz = parse_quiz(extract_tag("QUIZ", r_raw2) or r_raw2)
                if len(qz) >= 3:
                    p_res["quiz"] = qz
            m_p1 = [k for k in ["SIMPLE", "SUMMARY", "VILLAGE", "WORDS"] if k in p_res["missing"]]
            if m_p1:
                r_raw1, r_tc1 = backend.gen(p1, max_new=max_new)
                tok_cnt += r_tc1
                p_res1 = parse_resp(r_raw1)
                for k in ["simple", "summary", "village"]:
                    if not p_res[k] and p_res1[k]:
                        p_res[k] = p_res1[k]
                if not p_res["words"] and p_res1["words"]:
                    p_res["words"] = p_res1["words"]
            p_res["missing"] = [k for k in ["SIMPLE", "SUMMARY", "VILLAGE", "WORDS"] if not p_res[k.lower()]]
            if len(p_res["quiz"]) < 3:
                p_res["missing"].append("QUIZ")
            p_res["valid"] = len(p_res["missing"]) == 0

    readab = compare_readab(hard_s["text"], p_res["simple"]) if p_res["simple"] else None

    w_with_gl = []
    for item in p_res["words"]:
        gl_match = find_gl(item["word"], gl)
        w_with_gl.append({
            "word": item["word"],
            "meaning": item["meaning"],
            "gl": gl_match
        })

    chk_quiz = check_quiz(p_res["quiz"], s_list)

    return {
        "s_list": s_list,
        "hard_s": hard_s,
        "cand_words": cand_w,
        "parsed": p_res,
        "readab": readab,
        "words": w_with_gl,
        "quiz": chk_quiz,
        "tok_cnt": tok_cnt,
        "is_mock": getattr(backend, "is_mock", False)
    }
