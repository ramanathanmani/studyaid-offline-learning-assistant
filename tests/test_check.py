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
            "q": "What is the green pigment in plants?",
            "a": "Refraction",
            "c": "S2"
        },
        {
            "q": "Where does refraction occur?",
            "a": "Refraction",
            "c": "S1"
        }
    ]
    res = check_quiz(items, s_list)
    assert res[0]["status"] == "SUPPORTED"
    assert "refraction" in res[0]["shared"]
    assert "deviation" in res[0]["shared"]
    assert res[0]["suggested"] is None
    
    assert res[1]["status"] == "FLAGGED"
    assert res[1]["suggested"] == "S3"
    
    assert res[2]["status"] == "FLAGGED"
    assert res[2]["suggested"] is None

    assert res[3]["status"] == "SUPPORTED (exact term)"
    assert res[3]["shared"] == ["refraction"]
    assert res[3]["suggested"] is None

    assert res[4]["status"] == "FLAGGED"
    assert res[4]["suggested"] == "S2" or res[4]["suggested"] == "S3"

def test_stemming_and_word_forms():
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
    assert res[1]["status"] == "SUPPORTED (exact term)"
    assert res[2]["status"] == "SUPPORTED (exact term)"
    assert res[3]["status"] == "SUPPORTED (exact term)"

def test_answer_copied_guard():
    from studyaid.check import is_ans_too_long_or_copied
    c_txt = "The stomach secretes hydrochloric acid, which provides an acidic medium and activates pepsin."
    exact_ans = "The stomach secretes hydrochloric acid, which provides an acidic medium and activates pepsin."
    short_ans = "Secretes hydrochloric acid"
    too_long_ans = "one two three four five six seven eight nine ten eleven twelve thirteen"
    
    assert is_ans_too_long_or_copied(exact_ans, c_txt) is True
    assert is_ans_too_long_or_copied(too_long_ans, c_txt) is True
    assert is_ans_too_long_or_copied(short_ans, c_txt) is False
