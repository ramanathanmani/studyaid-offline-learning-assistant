import re

EXAMPLE_BANK = [
    {
        "id": "temperature_chennai_ooty",
        "topic": "temperature",
        "keywords": ["temperature", "kelvin", "celsius", "fahrenheit", "heat", "hotness", "coldness", "zero kelvin", "absolute zero", "triple point"],
        "example": "A Chennai afternoon in May reaches about 40 °C, while Ooty in winter drops to about 15 °C. A thermometer measures each condition as an objective number, just as a kitchen kettle shows boiling water reaching 100 °C."
    },
    {
        "id": "optics_water_tumbler",
        "topic": "optics",
        "keywords": ["refraction", "light", "lens", "lenses", "medium", "ray", "optical", "convex", "concave", "normal", "obliquely"],
        "example": "When a stainless steel spoon is placed in a clear glass tumbler of water at a village tea stall, the spoon appears broken or bent at the water boundary because light changes direction across different media."
    },
    {
        "id": "digestion_aattukkal",
        "topic": "digestion",
        "keywords": ["digestion", "stomach", "digestive", "enzyme", "amylase", "chyme", "intestine", "peristalsis", "villi", "bolus"],
        "example": "Just as a traditional village stone grinder (ஆட்டுக்கல் / aattukkal) grinds coarse lentils and rice into smooth, digestible batter, human digestive enzymes break down complex food into simple nutrient molecules."
    },
    {
        "id": "circuits_water_pipe",
        "topic": "electricity",
        "keywords": ["circuit", "current", "voltage", "conductor", "resistor", "resistance", "battery", "ampere", "potential difference", "ohm"],
        "example": "Water flowing from an overhead village storage tank through PVC pipes to a tap behaves like electric current flowing through copper wires driven by voltage potential across a circuit."
    },
    {
        "id": "sound_temple_bell",
        "topic": "sound",
        "keywords": ["sound", "wave", "waves", "vibration", "vibrating", "frequency", "compression", "rarefaction", "longitudinal", "acoustic"],
        "example": "When a large bronze temple bell is struck during evening prayers, its metal vibrates back and forth rapidly, creating alternating compression and rarefaction waves that travel through the air to our ears."
    },
    {
        "id": "photosynthesis_solar_crops",
        "topic": "photosynthesis",
        "keywords": ["photosynthesis", "chlorophyll", "chloroplast", "sunlight", "stomata", "leaves", "carbon dioxide", "glucose", "plant"],
        "example": "Just as a village solar water pump absorbs sunlight on its rooftop panels to draw water for green paddy fields, green leaves capture solar energy using chlorophyll to manufacture glucose and oxygen."
    }
]

def pick_bank_example(txt):
    low = txt.lower()
    best_ex = None
    best_score = 0
    for entry in EXAMPLE_BANK:
        score = sum(1 for kw in entry["keywords"] if re.search(r"\b" + re.escape(kw) + r"\b", low))
        if score > best_score:
            best_score = score
            best_ex = entry
    if best_ex and best_score >= 1:
        return best_ex["example"], best_ex["id"]
    return None, None
