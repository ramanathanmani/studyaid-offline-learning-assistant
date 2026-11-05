from studyaid.backend import MockBackend
from studyaid.gloss import load_gl
from studyaid.pipeline import run_pipeline

def test_pipeline_with_mock():
    txt = (
        "When a ray of light travels from one transparent medium into another obliquely, the path of the light undergoes deviation. "
        "This deviation of ray of light is called refraction. "
        "Refraction takes place due to the difference in the velocity of light in different media. "
        "The velocity of light is more in a rarer medium and less in a denser medium. "
        "When light travels from a denser medium into a rarer medium, the refracted ray is bent away from the normal drawn to the interface."
    )
    gl = {
        "refraction": {"en": "refraction", "ta": "ஒளிவிலகல்", "translit": "Oli-vilagal", "verified": False},
        "medium": {"en": "medium", "ta": "ஊடகம்", "translit": "Oodagam", "verified": False},
        "normal": {"en": "normal", "ta": "குத்துக்கோடு", "translit": "Kuthukkodu", "verified": False},
        "obliquely": {"en": "obliquely", "ta": "சாய்வாக", "translit": "Saaivaaga", "verified": False}
    }
    bk = MockBackend()
    res = run_pipeline(txt, bk, gl, two_pass=False)
    
    assert res["is_mock"] is True
    assert res["hard_s"]["id"] == "S1"
    assert res["parsed"]["valid"] is True
    assert len(res["quiz"]) >= 3
    assert res["readab"] is not None
    assert res["readab"]["orig"]["w_cnt"] == 20
    assert res["readab"]["simp"]["w_cnt"] == 12

def test_pipeline_two_pass():
    txt = (
        "When a ray of light travels from one transparent medium into another obliquely, the path of the light undergoes deviation. "
        "This deviation of ray of light is called refraction. "
        "Refraction takes place due to the difference in the velocity of light in different media. "
        "The velocity of light is more in a rarer medium and less in a denser medium. "
        "When light travels from a denser medium into a rarer medium, the refracted ray is bent away from the normal drawn to the interface."
    )
    gl = {}
    bk = MockBackend()
    res = run_pipeline(txt, bk, gl, two_pass=True)
    assert res["parsed"]["valid"] is True
    assert len(res["quiz"]) == 3
