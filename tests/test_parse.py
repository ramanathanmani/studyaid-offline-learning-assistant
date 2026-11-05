from studyaid.parse import parse_resp, parse_words, validate_quiz

def test_parse_good_reply():
    raw = (
        "<SIMPLE>When light enters water at a slant, it bends.</SIMPLE>\n"
        "<SUMMARY>Light bends when moving between media. Speed changes cause this bending.</SUMMARY>\n"
        "<VILLAGE>A bullock cart slows down when turning into mud.</VILLAGE>\n"
        "<WORDS>\n"
        "refraction | bending of light\n"
        "medium | substance light travels through\n"
        "</WORDS>\n"
        "<QUIZ>\n"
        "Q: What is refraction?\n"
        "A: Bending of light path\n"
        "C: S2\n"
        "Q: Why does it happen?\n"
        "A: Velocity of light differences\n"
        "C: S3\n"
        "Q: How does it bend?\n"
        "A: Away from normal interface\n"
        "C: S5\n"
        "</QUIZ>"
    )
    res = parse_resp(raw)
    assert res["valid"] is True
    assert len(res["missing"]) == 0
    assert res["simple"] == "When light enters water at a slant, it bends."
    assert len(res["words"]) == 2
    assert len(res["quiz"]) == 3
    assert res["quiz"][0]["c"] == "S2"

def test_parse_words_candidate_filter():
    raw_words = (
        "refraction | light bending at boundary\n"
        "rural | village life\n"
        "Tamil Nadu | southern state\n"
        "medium | optical material\n"
    )
    cands = ["refraction", "medium", "obliquely"]
    res = parse_words(raw_words, cand_words=cands)
    assert len(res) == 3
    assert res[0]["word"] == "refraction"
    assert res[0]["meaning"] == "light bending at boundary"
    assert res[1]["word"] == "medium"
    assert res[1]["meaning"] == "optical material"
    assert res[2]["word"] == "obliquely"
    assert res[2]["meaning"] == "no explanation generated"

def test_validate_quiz_guards():
    s_list = [
        ("S1", "When a ray of light travels from one transparent medium into another obliquely, the path of the light undergoes deviation."),
        ("S2", "This deviation of ray of light is called refraction.")
    ]
    items = [
        {
            "q": "When a ray of light travels from one transparent medium into another obliquely, the path of the light undergoes deviation.",
            "a": "Refraction",
            "c": "S1"
        },
        {
            "q": "What is refraction",
            "a": "Refraction",
            "c": "S2"
        },
        {
            "q": "What is the deviation of light called?",
            "a": "Refraction",
            "c": "S2"
        },
        {
            "q": "What causes light to bend at an interface?",
            "a": "Refraction",
            "c": "S2"
        },
        {
            "q": "Why does the path of light change across media?",
            "a": "Difference in velocity",
            "c": "S2"
        }
    ]
    val = validate_quiz(items, s_list)
    assert len(val) == 2
    assert val[0]["q"] == "What is the deviation of light called?"
    assert val[0]["a"] == "Refraction"
    assert val[1]["q"] == "Why does the path of light change across media?"
    assert val[1]["a"] == "Difference in velocity"

def test_parse_truncated_reply():
    raw = (
        "<SIMPLE>When light enters water at a slant, it bends.</SIMPLE>\n"
        "<SUMMARY>Light bends when moving between media."
    )
    res = parse_resp(raw)
    assert res["valid"] is False
    assert res["summary"] == "Light bends when moving between media."
    assert "VILLAGE" in res["missing"]
    assert "WORDS" in res["missing"]
    assert "QUIZ" in res["missing"]

def test_extract_tag_unclosed_and_variations():
    from studyaid.parse import extract_tag
    txt = (
        "<SIMPLE>Rewrite text here.\n"
        "<SUMMARY>Summary paragraph.\n"
        "<SVILLE>Village story in Thanjavur.\n"
        "<WORDS>refraction | light bending"
    )
    assert extract_tag("SIMPLE", txt) == "Rewrite text here."
    assert extract_tag("SUMMARY", txt) == "Summary paragraph."
    assert extract_tag("VILLAGE", txt) == "Village story in Thanjavur."
    assert "refraction | light bending" in extract_tag("WORDS", txt)

def test_validate_quiz_reject_citation_and_sentence_copy():
    s_list = [
        ("S1", "An electric current is defined as the rate of flow of electric charges across any cross section of a conductor.")
    ]
    items = [
        {"q": "What is current?", "a": "S1", "c": "S1"},
        {"q": "What is current?", "a": "An electric current is defined as the rate of flow of electric charges across any cross section of a conductor.", "c": "S1"},
        {"q": "What is current defined as?", "a": "rate of flow of electric charges", "c": "S1"}
    ]
    val = validate_quiz(items, s_list)
    assert len(val) == 1
    assert val[0]["a"] == "rate of flow of electric charges"

def test_parse_malformed_reply():
    raw = (
        "<SIMPLE></SIMPLE>\n"
        "<SUMMARY>Short summary</SUMMARY>\n"
        "<VILLAGE>Village tale</VILLAGE>\n"
        "<WORDS>word | meaning</WORDS>\n"
        "<QUIZ>\n"
        "Q: Only one question?\n"
        "A: Yes only one\n"
        "C: S1\n"
        "</QUIZ>"
    )
    res = parse_resp(raw)
    assert res["valid"] is False
    assert "SIMPLE" in res["missing"]
    assert "QUIZ" in res["missing"]
