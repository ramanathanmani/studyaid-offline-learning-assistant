def fmt_sents(s_list):
    return "\n".join(f"[{sid}] {txt}" for sid, txt in s_list)

def build_prompt(s_list, hard_s, hard_words, pass_mode=None):
    p_txt = fmt_sents(s_list)
    hw_str = ", ".join(hard_words[:5])
    
    if pass_mode == 1:
        return (
            "You are an offline study assistant for rural Tamil Nadu students (Class 8-10).\n"
            f"Passage:\n{p_txt}\n\n"
            f"Hardest Sentence ([{hard_s['id']}]): {hard_s['text']}\n"
            f"Candidate Hard Words: {hw_str}\n\n"
            "Respond using EXACTLY these tags (Pass 1 - do not include quiz):\n"
            "<SIMPLE>one plain-English rewrite of the given hardest sentence</SIMPLE>\n"
            "<SUMMARY>2-3 short sentences</SUMMARY>\n"
            "<VILLAGE>one everyday rural example, 3-4 sentences</VILLAGE>\n"
            "<WORDS>word | simple meaning (one line each)</WORDS>"
        )
    if pass_mode == 2:
        return (
            "You are an offline study assistant for rural Tamil Nadu students (Class 8-10).\n"
            f"Passage:\n{p_txt}\n\n"
            "Create exactly 3 quiz questions based on the passage.\n"
            "Respond using EXACTLY this tag (Pass 2 - only the quiz):\n"
            "<QUIZ>\n"
            "Q: question\n"
            "A: answer using words from the cited sentence\n"
            "C: S3\n"
            "</QUIZ>"
        )

    return (
        "You are an offline study assistant for rural Tamil Nadu students (Class 8-10).\n"
        f"Passage:\n{p_txt}\n\n"
        f"Hardest Sentence ([{hard_s['id']}]): {hard_s['text']}\n"
        f"Candidate Hard Words: {hw_str}\n\n"
        "Respond using EXACTLY this delimited format:\n"
        "<SIMPLE>one plain-English rewrite of the given hardest sentence</SIMPLE>\n"
        "<SUMMARY>2-3 short sentences</SUMMARY>\n"
        "<VILLAGE>one everyday rural example, 3-4 sentences</VILLAGE>\n"
        "<WORDS>word | simple meaning (one line each)</WORDS>\n"
        "<QUIZ>\n"
        "Q: question\n"
        "A: answer using words from the cited sentence\n"
        "C: S3\n"
        "</QUIZ>"
    )
