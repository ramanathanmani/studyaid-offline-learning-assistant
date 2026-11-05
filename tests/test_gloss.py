import os
from studyaid.gloss import norm_cand, load_gl, find_gl

def test_norm_cand():
    assert "refraction" in norm_cand("refractions")
    assert "medium" in norm_cand("mediums")
    assert "refract" in norm_cand("refracted")
    assert "bend" in norm_cand("bending")
    assert "oblique" in norm_cand("obliquely")

def test_glossary_hit_and_miss(tmp_path):
    p = tmp_path / "gl.json"
    p.write_text(
        '[{"en": "refraction", "ta": "ஒளிவிலகல்", "translit": "Oli-vilagal", "source": "test", "verified": false},'
        '{"en": "medium", "ta": "ஊடகம்", "translit": "Oodagam", "source": "test", "verified": false}]',
        encoding="utf-8"
    )
    gl = load_gl(str(p))
    hit = find_gl("refraction", gl)
    assert hit is not None
    assert hit["ta"] == "ஒளிவிலகல்"
    assert hit["translit"] == "Oli-vilagal"
    assert hit["verified"] is False
    
    hit_suffix = find_gl("mediums", gl)
    assert hit_suffix is not None
    assert hit_suffix["ta"] == "ஊடகம்"
    
    miss = find_gl("photosynthesis", gl)
    assert miss is None
