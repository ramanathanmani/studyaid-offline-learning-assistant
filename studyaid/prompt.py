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
            "3. <VILLAGE>: Write a 2-sentence everyday comparison between the main idea of this passage and a familiar village object or activity. Keep it simple and do not add new scientific facts. You may use a Tamil name as a style hint.\n"
            "Worked Example (unrelated topic - evaporation):\n"
            "When wet clothes are hung outside in the village sun, the water slowly disappears into the warm air. In the same way, heat causes liquid water to turn into invisible vapor.\n"
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
            "- Reuse key words from the passage in your answer.\n"
            "- Every question must have a different answer.\n"
            "- Cite the exact sentence ID where the answer appears (e.g. C: S2, C: S3, C: S5).\n\n"
            "Format:\n"
            "<QUIZ>\n"
            "Q: question?\n"
            "A: short answer under 12 words\n"
            "C: [sentence ID where answer appears]\n\n"
            "Q: question?\n"
            "A: short answer under 12 words\n"
            "C: [sentence ID where answer appears]\n\n"
            "Q: question?\n"
            "A: short answer under 12 words\n"
            "C: [sentence ID where answer appears]\n\n"
            "Q: question?\n"
            "A: short answer under 12 words\n"
            "C: [sentence ID where answer appears]\n"
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

def build_retry_village_prompt(concept_summary):
    sys_msg = "You are an educational assistant for rural students. Always respond in English only. Follow instructions strictly."
    usr_msg = (
        f"Topic summary: {concept_summary}\n\n"
        "Write a simple 2-sentence everyday comparison between this idea and a familiar village object or activity. Keep it simple and do not add new scientific facts.\n"
        "Respond with ONLY the comparison inside <VILLAGE>...</VILLAGE> tags."
    )
    return wrap_inst(sys_msg, usr_msg, seed="<VILLAGE>\n")

def build_retry_summary_prompt(s_list):
    p_txt = fmt_sents(s_list)
    sys_msg = "You are a concise educational assistant. Follow instructions strictly."
    usr_msg = (
        f"Passage:\n{p_txt}\n\n"
        "Write a simple 2-sentence summary of the main scientific points in the passage.\n"
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
