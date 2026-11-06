from studyaid.sents import split_sents
from studyaid.hard import find_hard_sents, extract_hard_words
from studyaid.gloss import load_gl
from studyaid.backend import MockBackend
from studyaid.pipeline import run_pipeline

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

def test_stem_collapsing():
    txt = "Digestion is vital because digesting food and having digested nutrients supports life."
    cands = extract_hard_words(txt)
    assert "digestion" in cands
    assert "digesting" not in cands
    assert "digested" not in cands

def test_ranking_glossary_first():
    gl = {
        "refraction": {"en": "refraction", "ta": "ஒளிவிலகல்", "translit": "Oli-vilagal", "verified": True, "meaning": "the bending of light when it passes from one material into another"}
    }
    txt = "Atmospheric electromagnetic disturbances cause refraction in transparent substances."
    cands = extract_hard_words(txt, gl)
    assert cands[0] == "refraction"

def test_glossary_meaning_overrides_model_meaning():
    gl = {
        "refraction": {
            "en": "refraction",
            "ta": "ஒளிவிலகல்",
            "translit": "Oli-vilagal",
            "verified": True,
            "meaning": "the bending of light when it passes from one material into another"
        }
    }
    txt = "When a ray of light travels into another obliquely, it undergoes refraction."
    bk = MockBackend()
    res = run_pipeline(txt, bk, gl, two_pass=True)
    words = res["words"]
    ref_item = next((w for w in words if w["word"] == "refraction"), None)
    assert ref_item is not None
    assert ref_item["meaning"] == "the bending of light when it passes from one material into another"
