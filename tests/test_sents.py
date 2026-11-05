from studyaid.sents import split_sents

def test_split_basic():
    txt = "This is first. This is second! Is this third? Yes."
    res = split_sents(txt)
    assert len(res) == 4
    assert res[0] == ("S1", "This is first.")
    assert res[1] == ("S2", "This is second!")
    assert res[2] == ("S3", "Is this third?")
    assert res[3] == ("S4", "Yes.")

def test_abbrev_and_decimals():
    txt = "Light travels at 3.0 speed in e.g. vacuum. That is fast."
    res = split_sents(txt)
    assert len(res) == 2
    assert res[0][0] == "S1"
    assert "3.0" in res[0][1]
    assert "e.g." in res[0][1]
    assert res[1] == ("S2", "That is fast.")

def test_optics_sample_sentences():
    txt = (
        "When a ray of light travels from one transparent medium into another obliquely, the path of the light undergoes deviation. "
        "This deviation of ray of light is called refraction. "
        "Refraction takes place due to the difference in the velocity of light in different media. "
        "The velocity of light is more in a rarer medium and less in a denser medium. "
        "When light travels from a denser medium into a rarer medium, the refracted ray is bent away from the normal drawn to the interface."
    )
    res = split_sents(txt)
    assert len(res) == 5
    assert res[0][0] == "S1"
    assert res[4][0] == "S5"
