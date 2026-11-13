import json
from pathlib import Path
from studyaid.gloss import load_gl, find_terms
from studyaid.check import check_quiz, check_item, generate_fallback_quiz, add_mcq_options
from studyaid.hard import check_number_preservation
from studyaid.example_bank import pick_bank_example
from studyaid.telem import collect_telem
from studyaid.readab import compare_readab
from studyaid.render import build_report

def test_glossary_correctness_and_regression():
    gl = load_gl(Path("data/glossary.json"))
    
    # Regression checks for fahrenheit, saturated, equilibrium
    assert "fahrenheit" in gl
    assert "32" in gl["fahrenheit"]["en_def"] and "212" in gl["fahrenheit"]["en_def"]
    
    assert "saturated vapour" in gl or "saturated" in gl
    sat_entry = gl.get("saturated vapour") or gl.get("saturated")
    assert "vapour" in sat_entry["en_def"].lower() or "maximum" in sat_entry["en_def"].lower()
    
    assert "equilibrium" in gl
    assert "balance" in gl["equilibrium"]["en_def"].lower()
    
    # Check rendered report has no "English only"
    pipe_res = {
        "is_mock": True,
        "s_list": [("S1", "Sentence 1")],
        "hard_s": {"id": "S1", "text": "Sentence 1"},
        "parsed": {"simple": "Sentence 1", "summary": "- Point 1 [S1]", "village": "Example"},
        "readab": None,
        "words": [
            {"word": "fahrenheit", "meaning": "scale", "gl": gl["fahrenheit"]},
            {"word": "equilibrium", "meaning": "state", "gl": gl["equilibrium"]}
        ],
        "quiz": []
    }
    telem_res = collect_telem("test_model", None, 10, 1.0, is_mock=True)
    rep = build_report(pipe_res, telem_res)
    assert "English only" not in rep
    assert "பாரன்ஹீட்" in rep
    assert "சமநிலை" in rep

def test_missing_term_graceful_handling():
    pipe_res = {
        "is_mock": True,
        "s_list": [("S1", "Sentence 1")],
        "hard_s": {"id": "S1", "text": "Sentence 1"},
        "parsed": {"simple": "Sentence 1", "summary": "- Point 1 [S1]", "village": "Example"},
        "readab": None,
        "words": [
            {"word": "quantum_nonexistent_xyz", "meaning": "some meaning", "gl": None}
        ],
        "quiz": []
    }
    telem_res = collect_telem("test_model", None, 10, 1.0, is_mock=True)
    rep = build_report(pipe_res, telem_res)
    assert "no Tamil entry yet" in rep
    assert "English only" not in rep

def test_number_preservation_guard():
    orig = "One kelvin is the fraction (1/273.16) of the thermodynamic temperature of the triple point of water."
    good_simp = "The triple point of water is the equilibrium point. One kelvin is 1/273.16 of that temperature."
    bad_simp = "The triple point of water is the equilibrium point. One kelvin is a fraction of that temperature."
    
    ok_good, missing_good = check_number_preservation(orig, good_simp)
    assert ok_good is True
    assert missing_good == []
    
    ok_bad, missing_bad = check_number_preservation(orig, bad_simp)
    assert ok_bad is False
    assert "273.16" in missing_bad

def test_example_bank_curated_facts():
    ex_temp, ex_id = pick_bank_example("Temperature is measured in kelvin and degree celsius.")
    assert "Chennai" in ex_temp or "thermometer" in ex_temp or "kettle" in ex_temp
    assert "Kumbakonam hot springs" not in ex_temp
    assert "temperature" in ex_id
    
    ex_opt, ex_id_opt = pick_bank_example("Refraction occurs when light enters a glass tumbler.")
    assert "glass" in ex_opt or "tumbler" in ex_opt or "light" in ex_opt
    assert "optics" in ex_id_opt

def test_quiz_fallback_guarantees_minimum_3_questions():
    sents = [
        ("S1", "Temperature is the measure of hotness or coldness of a body."),
        ("S2", "SI unit of temperature is kelvin."),
        ("S3", "One kelvin is the fraction 1/273.16 of the triple point of water."),
        ("S4", "Zero kelvin is known as absolute zero.")
    ]
    gl = load_gl(Path("data/glossary.json"))
    
    model_quiz = [
        {"q": "What is the unit of temperature?", "a": "kelvin", "c": "S2", "status": "SUPPORTED", "shared": ["temperature", "kelvin"]}
    ]
    
    fallback = generate_fallback_quiz(sents, model_quiz, gl, target_cnt=3)
    assert len(model_quiz) + len(fallback) >= 3
    
    total_quiz = model_quiz + fallback
    add_mcq_options(total_quiz, gl)
    for item in total_quiz:
        assert "opts" in item
        assert len(item["opts"]) == 4

def test_readability_metrics_table():
    orig = "One kelvin is the fraction (1/273.16) of the thermodynamic temperature of the triple point of water."
    simp = "One kelvin is the temperature at which water, vapor, and ice are in equilibrium."
    gl = load_gl(Path("data/glossary.json"))
    
    comp = compare_readab(orig, simp, gl)
    assert "diff" in comp
    assert "flesch_diff" in comp["diff"]
    assert "gl_chg" in comp["diff"]
    assert "w_per_s_chg" in comp["diff"]
    assert "syl_chg" in comp["diff"]
