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
    hw_lines = "\n".join(f"- {w}" for w in hard_words[:5])
    sys_msg = (
        "You are an offline smart study assistant for rural Tamil Nadu students (Class 8-10). "
        "Follow instructions strictly. Always output using the exact XML tags specified."
    )
    
    if pass_mode == 1:
        usr_msg = (
            f"Passage:\n{p_txt}\n\n"
            f"Hardest Sentence ([{hard_s['id']}]): {hard_s['text']}\n\n"
            f"Candidate Words to explain:\n{hw_lines}\n\n"
            "Instructions:\n"
            "1. <SIMPLE>: Rewrite the hardest sentence in fewer words than the original. Use common everyday words. Keep exactly one sentence.\n"
            "2. <SUMMARY>: Write a 2-3 sentence simple summary of the passage.\n"
            "3. <VILLAGE>: Write an everyday rural example (3-4 sentences) that directly explains the scientific concepts in the passage using real village situations.\n"
            "Worked Example for Village (different topic):\n"
            "Concept: Friction opposes motion.\n"
            "Example: In an agricultural village near Thanjavur, farmer Murugan pulls a wooden plow across wet paddy fields. The thick clay exerts heavy friction against the plow blade, requiring his two bullocks to pull with greater force.\n"
            "4. <WORDS>: Explain ONLY the candidate words listed above, one line per word in format:\n"
            "word | simple meaning in under 12 words\n\n"
            "Output using exact tags:"
        )
        return wrap_inst(sys_msg, usr_msg, seed="<SIMPLE>")

    if pass_mode == 2:
        usr_msg = (
            f"Passage:\n{p_txt}\n\n"
            "Instructions:\n"
            "Create 4 short quiz questions and concise answers based on the passage above.\n"
            "Rules:\n"
            "- Every question must start with What, Why, How, or Which and end with '?'.\n"
            "- Do NOT copy whole passage sentences as questions.\n"
            "- Answer must be a short phrase (under 12 words), NOT a whole passage sentence.\n"
            "- Reuse key words from the cited sentence in your answer.\n"
            "- Every question must have a different answer.\n"
            "- Cite the exact sentence ID (e.g. C: S1, C: S2).\n\n"
            "Format:\n"
            "<QUIZ>\n"
            "Q: question?\n"
            "A: short answer under 12 words\n"
            "C: S1\n\n"
            "Q: question?\n"
            "A: short answer under 12 words\n"
            "C: S2\n\n"
            "Q: question?\n"
            "A: short answer under 12 words\n"
            "C: S3\n\n"
            "Q: question?\n"
            "A: short answer under 12 words\n"
            "C: S4\n"
            "</QUIZ>"
        )
        return wrap_inst(sys_msg, usr_msg, seed="<QUIZ>\nQ:")

    usr_msg = (
        f"Passage:\n{p_txt}\n\n"
        f"Hardest Sentence ([{hard_s['id']}]): {hard_s['text']}\n\n"
        f"Candidate Words:\n{hw_lines}\n\n"
        "Produce <SIMPLE>, <SUMMARY>, <VILLAGE>, <WORDS>, and <QUIZ> sections."
    )
    return wrap_inst(sys_msg, usr_msg, seed="<SIMPLE>")

def build_retry_simple_prompt(orig_s_text, bad_simple):
    sys_msg = "You are a concise educational assistant. Follow instructions strictly."
    usr_msg = (
        f"Original sentence ({len(orig_s_text.split())} words):\n{orig_s_text}\n\n"
        "Rewrite in fewer words than the original. Use common everyday words. Keep one sentence.\n"
        "Respond with ONLY the rewritten sentence inside <SIMPLE>...</SIMPLE> tags."
    )
    return wrap_inst(sys_msg, usr_msg, seed="<SIMPLE>")

def build_retry_village_prompt(key_s_text):
    sys_msg = "You are an educational assistant for rural students. Always respond in English only. Follow instructions strictly."
    usr_msg = (
        f"Key concept sentence:\n{key_s_text}\n\n"
        "Write an everyday village-life example in English (2-3 sentences) directly illustrating this concept. "
        "Use everyday rural Tamil Nadu settings (e.g. well, paddy field, bullock cart, farmer Murugan). Write in English only.\n"
        "Respond with ONLY the example inside <VILLAGE>...</VILLAGE> tags."
    )
    return wrap_inst(sys_msg, usr_msg, seed="<VILLAGE>\nIn a village")

def build_retry_summary_prompt(s_list):
    p_txt = fmt_sents(s_list)
    sys_msg = "You are a concise educational assistant. Follow instructions strictly."
    usr_msg = (
        f"Passage:\n{p_txt}\n\n"
        "Write a simple 2-3 sentence summary of the main scientific points in the passage.\n"
        "Respond with ONLY the summary inside <SUMMARY>...</SUMMARY> tags."
    )
    return wrap_inst(sys_msg, usr_msg, seed="<SUMMARY>")

def build_retry_words_prompt(cand_words):
    hw_lines = "\n".join(f"- {w}" for w in cand_words[:5])
    sys_msg = "You are a concise educational assistant. Follow instructions strictly."
    usr_msg = (
        f"Words to explain:\n{hw_lines}\n\n"
        "Explain each word in simple everyday English (under 12 words each).\n"
        "Format (one line per word):\n"
        "word | simple meaning\n\n"
        "Respond inside <WORDS>...</WORDS> tags."
    )
    return wrap_inst(sys_msg, usr_msg, seed="<WORDS>\n")
