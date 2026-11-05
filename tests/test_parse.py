from studyaid.parse import parse_resp

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

def test_parse_truncated_reply():
    raw = (
        "<SIMPLE>When light enters water at a slant, it bends.</SIMPLE>\n"
        "<SUMMARY>Light bends when moving between media."
    )
    res = parse_resp(raw)
    assert res["valid"] is False
    assert "SUMMARY" in res["missing"]
    assert "VILLAGE" in res["missing"]
    assert "WORDS" in res["missing"]
    assert "QUIZ" in res["missing"]

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
