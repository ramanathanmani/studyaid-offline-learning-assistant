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
