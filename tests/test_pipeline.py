from studyaid.backend import MockBackend
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
    res = run_pipeline(txt, bk, gl, two_pass=True)
    
    assert res["is_mock"] is True
    assert res["hard_s"]["id"] == "S1"
    assert res["parsed"]["valid"] is True
    assert len(res["quiz"]) >= 3
    assert res["readab"] is not None
    assert res["readab"]["orig"]["w_cnt"] == 20
    assert res["guards"]["rewrite_shorter"] is True
    assert res["guards"]["village_format_ok"] is True
    assert res["guards"]["quiz_supported_cnt"] >= 2
    assert res["guards"]["words_explained_cnt"] <= 5

def test_pipeline_simplification_fallback():
    class BadSimpBackend:
        def __init__(self):
            self.is_mock = True
        def gen(self, prompt, max_new=480):
            p_low = prompt.lower()
            if "pass_mode=2" in p_low or "<quiz>" in p_low:
                return "<QUIZ>\nQ: What is refraction?\nA: refraction\nC: S2\nQ: What causes it?\nA: difference in velocity\nC: S3\nQ: How does it bend?\nA: away from normal\nC: S5\n</QUIZ>", 50
            return "<SIMPLE>This is a ridiculously long rewrite that contains many more words than the original sentence could ever possibly contain in order to trigger the guard.</SIMPLE><SUMMARY>Sum</SUMMARY><VILLAGE>Bullock cart deviates from normal path.</VILLAGE><WORDS>refraction | bending</WORDS>", 50

    txt = "Short sentence. Another sentence."
    bk = BadSimpBackend()
    res = run_pipeline(txt, bk, {}, two_pass=True)
    assert res["guards"]["no_simpler_rewrite"] is True
    assert res["readab"]["orig"]["w_cnt"] == res["readab"]["simp"]["w_cnt"]

def test_pipeline_summary_fallback():
    class NoSummaryBackend:
        def __init__(self):
            self.is_mock = True
        def gen(self, prompt, max_new=480):
            p_low = prompt.lower()
            if "quiz" in p_low:
                return "<QUIZ>\nQ: What is sentence one?\nA: first sentence\nC: S1\nQ: What is sentence two?\nA: second sentence\nC: S2\nQ: What is sentence three?\nA: third sentence\nC: S3\n</QUIZ>", 40
            return "<SIMPLE>A short sentence.</SIMPLE><VILLAGE>Farmer Murugan pulls plow in wet paddy field causing deviation.</VILLAGE><WORDS>sentence | line</WORDS>", 40

    txt = "First sentence here. Second sentence follows. Third sentence ends."
    bk = NoSummaryBackend()
    res = run_pipeline(txt, bk, {}, two_pass=True)
    summary = res["parsed"]["summary"]
    assert "fallback: first sentences of the passage" in summary
    assert "First sentence here." in summary
    assert "Second sentence follows." in summary
    assert res["guards"]["summary_produced_without_fallback"] is False
