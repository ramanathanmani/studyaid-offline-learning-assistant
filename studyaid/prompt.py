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
            "Example: When a bullock cart moves from a smooth tar road onto loose sand, the cart wheels experience heavy friction, making the bullocks pull harder.\n"
            "4. <WORDS>: Explain ONLY the candidate words listed above, one line per word in format:\n"
            "word | simple meaning in under 12 words\n\n"
            "Output using exact tags:"
        )
        return wrap_inst(sys_msg, usr_msg, seed="<SIMPLE>")

    if pass_mode == 2:
        usr_msg = (
            f"Passage:\n{p_txt}\n\n"
            "Instructions:\n"
            "Create exactly 3 quiz questions based on the cited sentences from the passage.\n"
            "Rules:\n"
            "- Every question must end with '?'. Do NOT copy passage sentences as questions.\n"
            "- Reuse exact words from the cited sentence in your answer.\n"
            "- Every question must have a different answer.\n"
            "- Cite the exact sentence ID (e.g. S1, S2).\n\n"
            "Worked Example (different topic - water cycle):\n"
            "Passage excerpt: [S1] Water evaporates from lakes when heated by solar radiation. [S2] Rising vapor condenses into clouds.\n"
            "Q: What happens to lake water when it is heated by solar radiation?\n"
            "A: Evaporates\n"
            "C: S1\n\n"
            "Now produce 3 quiz items using EXACTLY this format:\n"
            "<QUIZ>\n"
            "Q: question?\n"
            "A: answer\n"
            "C: S1\n\n"
            "Q: question?\n"
            "A: answer\n"
            "C: S2\n\n"
            "Q: question?\n"
            "A: answer\n"
            "C: S3\n"
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
    sys_msg = "You are an educational assistant for rural students. Follow instructions strictly."
    usr_msg = (
        f"Key concept sentence:\n{key_s_text}\n\n"
        "Write an everyday village-life example (2-3 sentences) directly illustrating this concept. "
        "You must explicitly mention the scientific terms and events from the concept sentence.\n"
        "Respond with ONLY the example inside <VILLAGE>...</VILLAGE> tags."
    )
    return wrap_inst(sys_msg, usr_msg, seed="<VILLAGE>")
