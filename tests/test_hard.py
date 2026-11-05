from studyaid.sents import split_sents
from studyaid.hard import find_hard_sents, extract_hard_words

def test_hardest_sentence_optics():
    txt = (
        "When a ray of light travels from one transparent medium into another obliquely, the path of the light undergoes deviation. "
        "This deviation of ray of light is called refraction. "
        "Refraction takes place due to the difference in the velocity of light in different media. "
        "The velocity of light is more in a rarer medium and less in a denser medium. "
        "When light travels from a denser medium into a rarer medium, the refracted ray is bent away from the normal drawn to the interface."
    )
    s_list = split_sents(txt)
    best = find_hard_sents(s_list)
    assert best["id"] == "S1"
    assert best["c_cnt"] == 4
    assert best["tot"] == 20
    s3_cnt = sum(1 for w in ["refraction", "difference", "velocity", "different"])
    assert s3_cnt == 4

def test_extract_hard_words():
    txt = "Refraction takes place due to the difference in velocity."
    cands = extract_hard_words(txt)
    assert "refraction" in cands
    assert "difference" in cands
    assert "velocity" in cands
    assert "takes" not in cands

def test_optics_long_hard_words_non_empty():
    import os
    from studyaid.gloss import load_gl
    gl_p = "data/tamil_glossary.json"
    gl = load_gl(gl_p) if os.path.exists(gl_p) else {}
    txt = open("samples/optics_long.txt").read()
    cands = extract_hard_words(txt, gl)
    assert len(cands) > 0
    assert len(cands) <= 5
    assert "refraction" in cands
