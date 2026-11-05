def fmt_sents(s_list):
    return "\n".join(f"[{sid}] {txt}" for sid, txt in s_list)

def wrap_inst(sys_msg, usr_msg, seed=""):
    return (
        f"<|start_header_id|>system<|end_header_id|>\n\n{sys_msg}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n{usr_msg}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n{seed}"
    )

def build_prompt(s_list, hard_s, hard_words, pass_mode=None):
    p_txt = fmt_sents(s_list)
    hw_str = ", ".join(hard_words[:5])
    sys_msg = (
        "You are an offline smart study assistant for rural Tamil Nadu students (Class 8-10). "
        "Follow instructions strictly. Always output using the exact XML tags specified."
    )
    
    if pass_mode == 1:
        usr_msg = (
            f"Passage:\n{p_txt}\n\n"
            f"Hardest Sentence ([{hard_s['id']}]): {hard_s['text']}\n"
            f"Candidate Hard Words: {hw_str}\n\n"
            "Produce the following sections using exact tags (do not include quiz):\n"
            "<SIMPLE>one plain-English rewrite of the given hardest sentence</SIMPLE>\n"
            "<SUMMARY>2-3 short sentences</SUMMARY>\n"
            "<VILLAGE>one everyday rural example, 3-4 sentences</VILLAGE>\n"
            "<WORDS>\nword | simple meaning (one line each)\n</WORDS>"
        )
        return wrap_inst(sys_msg, usr_msg, seed="<SIMPLE>")

    if pass_mode == 2:
        usr_msg = (
            f"Passage:\n{p_txt}\n\n"
            "Create exactly 3 quiz questions based on the cited sentences from the passage.\n"
            "Respond using EXACTLY this tag:\n"
            "<QUIZ>\n"
            "Q: question\n"
            "A: answer using words from the cited sentence\n"
            "C: S3\n\n"
            "Q: question\n"
            "A: answer using words from the cited sentence\n"
            "C: S2\n\n"
            "Q: question\n"
            "A: answer using words from the cited sentence\n"
            "C: S5\n"
            "</QUIZ>"
        )
        return wrap_inst(sys_msg, usr_msg, seed="<QUIZ>\nQ:")

    usr_msg = (
        f"Passage:\n{p_txt}\n\n"
        f"Hardest Sentence ([{hard_s['id']}]): {hard_s['text']}\n"
        f"Candidate Hard Words: {hw_str}\n\n"
        "Respond using EXACTLY this delimited format:\n"
        "<SIMPLE>one plain-English rewrite of the given hardest sentence</SIMPLE>\n"
        "<SUMMARY>2-3 short sentences</SUMMARY>\n"
        "<VILLAGE>one everyday rural example, 3-4 sentences</VILLAGE>\n"
        "<WORDS>\nword | simple meaning (one line each)\n</WORDS>\n"
        "<QUIZ>\n"
        "Q: question 1\n"
        "A: answer using words from the cited sentence\n"
        "C: S3\n\n"
        "Q: question 2\n"
        "A: answer using words from the cited sentence\n"
        "C: S2\n\n"
        "Q: question 3\n"
        "A: answer using words from the cited sentence\n"
        "C: S5\n"
        "</QUIZ>"
    )
    return wrap_inst(sys_msg, usr_msg, seed="<SIMPLE>")
