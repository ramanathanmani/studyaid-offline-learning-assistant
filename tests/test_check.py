from studyaid.check import check_quiz

def test_check_supported_and_flagged():
    s_list = [
        ("S1", "When a ray of light travels from one transparent medium into another obliquely, the path undergoes deviation."),
        ("S2", "This deviation of ray of light is called refraction."),
        ("S3", "Refraction takes place due to the difference in the velocity of light in different media.")
    ]
    items = [
        {
            "q": "What is the deviation of light called?",
            "a": "Deviation of ray of light is refraction",
            "c": "S2"
        },
        {
            "q": "What causes the bending?",
            "a": "Difference in velocity across media",
            "c": "S1"
        },
        {
            "q": "Why does it happen?",
            "a": "Completely random phenomenon",
            "c": "S3"
        },
        {
            "q": "What is the term for light deviation?",
            "a": "Refraction",
            "c": "S2"
        }
    ]
    res = check_quiz(items, s_list)
    assert "SUPPORTED" in res[0]["status"]
    assert res[0]["c"] == "S2"
    assert res[0]["model_cite_correct"] is True
    
    assert "SUPPORTED" in res[1]["status"]
    assert res[1]["c"] == "S3"
    assert res[1]["auto_corrected"] is True
    assert res[1]["model_cite_correct"] is False
    assert res[1]["suggested"] == "S3"
    
    assert res[2]["status"] == "FLAGGED"
    assert res[2]["suggested"] is None

    assert res[3]["status"] == "SUPPORTED (exact term)"
    assert res[3]["c"] == "S2"

def test_digestion_q1_resolves_to_s2_not_s1():
    s_list = [
        ("S1", "Digestion is the biochemical breakdown of complex insoluble food substances into simple absorbable nutrient molecules required by living cells."),
        ("S2", "The human digestive process commences inside the buccal cavity, where teeth mechanically masticate solid food and salivary glands secrete the enzyme salivary amylase to break down complex starch into simple sugars.")
    ]
    items = [
        {
            "q": "What is the primary function of salivary amylase in the human digestive process?",
            "a": "Digests complex starch into simple sugars.",
            "c": "S1"
        }
    ]
    res = check_quiz(items, s_list)
    assert res[0]["c"] == "S2"
    assert res[0]["model_cite"] == "S1"
    assert res[0]["auto_corrected"] is True
    assert res[0]["model_cite_correct"] is False
    assert "SUPPORTED" in res[0]["status"]

def test_stemming_and_word_forms_optics():
    s_list = [
        ("S2", "This deviation of ray of light is called refraction."),
        ("S6", "Concave lenses diverge incident rays outward, consistently forming upright images.")
    ]
    items = [
        {"q": "What is the deviation called?", "a": "Refraction", "c": "S2"},
        {"q": "What do concave lenses do?", "a": "Diverges", "c": "S6"},
        {"q": "What do lenses do?", "a": "Diverged", "c": "S6"},
        {"q": "What is the action?", "a": "Diverging", "c": "S6"}
    ]
    res = check_quiz(items, s_list)
    assert res[0]["status"] == "SUPPORTED (exact term)"
    assert res[0]["c"] == "S2"
    assert res[1]["status"] == "SUPPORTED (exact term)"
    assert res[1]["c"] == "S6"
    assert res[2]["status"] == "SUPPORTED (exact term)"
    assert res[2]["c"] == "S6"
    assert res[3]["status"] == "SUPPORTED (exact term)"
    assert res[3]["c"] == "S6"

def test_no_sentence_qualifies():
    s_list = [
        ("S1", "Light travels in straight lines."),
        ("S2", "Refraction happens at interfaces.")
    ]
    items = [
        {"q": "What is the capital of France?", "a": "Paris", "c": "S1"}
    ]
    res = check_quiz(items, s_list)
    assert res[0]["status"] == "FLAGGED"
    assert res[0]["suggested"] is None
    assert res[0]["model_cite_correct"] is False

def test_answer_copied_guard():
    from studyaid.check import is_ans_too_long_or_copied
    c_txt = "The stomach secretes hydrochloric acid, which provides an acidic medium and activates pepsin."
    exact_ans = "The stomach secretes hydrochloric acid, which provides an acidic medium and activates pepsin."
    short_ans = "Secretes hydrochloric acid"
    too_long_ans = "one two three four five six seven eight nine ten eleven twelve thirteen"
    
    assert is_ans_too_long_or_copied(exact_ans, c_txt) is True
    assert is_ans_too_long_or_copied(too_long_ans, c_txt) is True
    assert is_ans_too_long_or_copied(short_ans, c_txt) is False
