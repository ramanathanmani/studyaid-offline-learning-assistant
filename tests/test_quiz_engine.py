import pytest
from studyaid.check import check_quiz, generate_fallback_quiz, add_mcq_options

def test_quiz_deterministic_fallback():
    s_list = [
        ("S1", "Temperature is the measure of hotness or coldness of a body."),
        ("S2", "SI unit of temperature is kelvin (K)."),
        ("S3", "One kelvin is the fraction of thermodynamic temperature of the triple point of water."),
        ("S4", "Zero kelvin (0 K) is commonly known as absolute zero."),
        ("S5", "The other units for measuring temperature are degree celsius and fahrenheit.")
    ]
    gl = {
        "temperature": {"ta": "வெப்பநிலை", "en_def": "How hot or cold something is"},
        "kelvin": {"ta": "கெல்வின்", "en_def": "The SI unit of temperature"},
        "absolute zero": {"ta": "தனிச் சுழி வெப்பநிலை", "en_def": "0 K"}
    }
    short_quiz = [
        {"q": "What is the unit of temperature?", "a": "kelvin", "c": "S2"}
    ]
    full_quiz = generate_fallback_quiz(s_list, short_quiz, gl, target_cnt=3)
    assert len(full_quiz) >= 3
    assert any("Fill in the blank" in q["q"] for q in full_quiz)

def test_quiz_mcq_distractors():
    gl = {
        "kelvin": {"en": "Kelvin", "ta": "கெல்வின்"},
        "celsius": {"en": "Degree Celsius", "ta": "டிகிரி செல்சியஸ்"},
        "fahrenheit": {"en": "Fahrenheit", "ta": "பாரன்ஹீட்"},
        "absolute zero": {"en": "Absolute zero", "ta": "தனிச் சுழி"}
    }
    quiz = [{"q": "What is the SI unit?", "a": "Kelvin", "c": "S2"}]
    add_mcq_options(quiz, gl)
    assert "opts" in quiz[0]
    assert len(quiz[0]["opts"]) == 4
    assert quiz[0]["opts"][0] == "Kelvin"

def test_support_whole_words():
    s_list = [("S5", "The other units for measuring temperature are degree celsius and fahrenheit.")]
    item = {"q": "What are the other units?", "a": "degree celsius and fahrenheit", "c": "S5"}
    checked = check_quiz([item], s_list)[0]
    assert checked["status"] == "SUPPORTED"
    # Shared should contain whole words, not stemmed fragments
    for w in checked["shared"]:
        assert w in ["celsius", "degree", "fahrenheit", "units", "measuring", "temperature"]
