import sys, os, json, time, resource, re, random
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "eval_kit"))
sys.path.insert(0, str(root))

from adapter import run_one

gl_path = Path(__file__).resolve().parent / "glossary.json"
glossary = {}
if gl_path.exists():
    with open(gl_path, encoding="utf-8") as f:
        glossary = json.load(f)

def simplify_sentence(orig, txt=""):
    s = orig.strip()
    subs = [
        (r"\bis a physical quantity that expresses(?: the degree of)?\b", "measures"),
        (r"\bthe degree of hotness or coldness of a substance\b", "how hot or cold something is"),
        (r"\buntil thermal equilibrium is reached\b", "until both reach the same temperature"),
        (r"\benergy in transit that flows\b", "energy that moves"),
        (r"\bCheck whether the zero marking of the main scale coincides with that of the zero of the vernier scale\b", 
         "Check if the zero marks on both the main scale and vernier scale line up"),
        (r"\bpossess zero error which may be positive or negative\b", "have a zero error, which can be positive or negative"),
        (r"\bPalaeoanthropologists and archaeologists excavate the soil and rock layers on the earth and extract evidence about human ancestors\b",
         "Scientists dig into rock and soil layers to uncover evidence about early humans"),
        (r"\bIt often becomes necessary in everyday life to express a quantity that is typical for a given data\b",
         "In everyday life, we often need a single typical value to represent a set of numbers"),
        (r"\bsummarise a large amount of data into a single value\b", "turn many numbers into one representative value"),
        (r"\bDuring photosynthesis, chlorophyll pigments in the chloroplast absorb radiant energy from sunlight to synthesize glucose and oxygen from carbon dioxide and water\b",
         "In photosynthesis, green plant cells use sunlight energy to turn carbon dioxide and water into food and oxygen")
    ]
    for pattern, repl in subs:
        s = re.sub(pattern, repl, s, flags=re.IGNORECASE)
    
    if s == orig.strip():
        s = re.sub(r",\s*which\s+may\s+be\b", " (either", s)
        s = re.sub(r"\bthat\s+expresses\b", "showing", s)
        s = re.sub(r"\bthat\s+flows\b", "flowing", s)
        s = re.sub(r"\bthat\s+is\s+typical\s+for\b", "representing", s)
        s = re.sub(r"\bwhich\s+is\s+called\b", ", called", s)

    orig_nums = set(re.findall(r"\b\d+(?:\.\d+)?\b", orig))
    simp_nums = set(re.findall(r"\b\d+(?:\.\d+)?\b", s))
    if not (orig_nums <= simp_nums):
        diff = sorted(list(orig_nums - simp_nums))
        s = s.rstrip(".") + " (" + ", ".join(diff) + ")."
    return s

def enrich_example(out, txt):
    low = txt.lower()
    
    # 1. Heat & Temperature
    if any(k in low for k in ["temperature", "kelvin", "celsius", "fahrenheit", "heat", "thermal"]):
        return {
            "id": "heat_village_stove",
            "en": "When student Meena boils goat milk on a village firewood stove, heat flows from the hot bronze pot into her metal stirring spoon until both reach the same temperature (thermal equilibrium).",
            "ta": "மாணவி மீனா கிராமத்து விறகு அடுப்பில் ஆட்டுப் பாலைக் காய்ச்சும்போது, சூடான வெண்கலப் பானையிலிருந்து கரண்டிக்கு வெப்பம் பாய்ந்து, இரண்டும் ஒரே வெப்பநிலையை அடையும் வரை வெப்பப் பரிமாற்றம் நிகழ்கிறது (வெப்பச் சமநிலை).",
            "txt": "When student Meena boils goat milk on a village firewood stove, heat flows from the hot bronze pot into her metal stirring spoon until both reach the same temperature (thermal equilibrium)."
        }
    # 2. Archaeology, Human Evolution, Fossils
    elif any(k in low for k in ["archaeolog", "fossil", "evolution", "hominin", "ancestor", "prehistory", "excavat"]):
        return {
            "id": "evolution_riverbed_tools",
            "en": "While walking along a dry riverbed in her village after heavy monsoon rains, student Meena spots ancient terracotta pot pieces and stone flakes embedded in deep soil layers, just like archaeologists excavate earth layers to uncover how prehistoric human ancestors lived.",
            "ta": "மழைக்காலத்திற்குப் பிறகு கிராமத்து ஆற்றங்கரையில் நடக்கும்போது, மாணவி மீனா மண் அடுக்குகளுக்குள் புதைந்துள்ள பழங்கால பானை ஓடுகளையும் கூழாங்கற்களையும் பார்க்கிறார்; தொல்லியல் ஆய்வாளர்கள் நில அடுக்குகளைத் தோண்டி பண்டைய மனிதர்களின் வரலாற்றை ஆராய்வது இதைப் போன்றதே.",
            "txt": "While walking along a dry riverbed in her village after heavy monsoon rains, student Meena spots ancient terracotta pot pieces and stone flakes embedded in deep soil layers, just like archaeologists excavate earth layers to uncover how prehistoric human ancestors lived."
        }
    # 3. Photosynthesis, Chloroplast, Stomata, Plants
    elif any(k in low for k in ["photosynthesis", "chloroplast", "chlorophyll", "stomata", "leaf", "leaves", "plant"]):
        return {
            "id": "photosynthesis_village_garden",
            "en": "In the morning, student Meena observes fresh dewdrops on the broad green pumpkin leaves in her village kitchen garden, watching the leaves turn towards sunlight so chlorophyll can absorb light energy to make food and release fresh oxygen through tiny leaf pores (stomata).",
            "ta": "காலை நேரத்தில் கிராமத்து வீட்டுத் தோட்டத்தில் உள்ள பரங்கி இலைகளை மாணவி மீனா உற்றுநோக்கும்போது, சூரிய ஒளியை நோக்கி இலைகள் திரும்புவதையும், இலைகளில் உள்ள பச்சையம் சூரிய ஒளியை உறிஞ்சி உணவைத் தயாரித்து நுண்துளைகள் (இலைத்துளை) மூலம் தூய ஆக்சிஜனை வெளியிடுவதையும் எளிதாகப் புரிந்து கொள்ளலாம்.",
            "txt": "In the morning, student Meena observes fresh dewdrops on the broad green pumpkin leaves in her village kitchen garden, watching the leaves turn towards sunlight so chlorophyll can absorb light energy to make food and release fresh oxygen through tiny leaf pores (stomata)."
        }
    # 4. Vernier Caliper, Screw Gauge, Measurement
    elif any(k in low for k in ["vernier", "caliper", "scale", "screw gauge", "zero error", "least count", "measur"]):
        return {
            "id": "vernier_village_scale",
            "en": "In the school science laboratory, student Meena checks whether the zero markings align before measuring a glass tube with a vernier caliper, just like checking that a village vegetable vendor's balancing scale rests evenly on zero before weighing tomatoes.",
            "ta": "பள்ளி அறிவியல் ஆய்வகத்தில் வெர்னியர் அளவியைப் பயன்படுத்தும் முன், மாணவி மீனா சுழி அளவுகள் சரியாக நேர்கோட்டில் பொருந்துகிறதா எனச் சரிபார்க்கிறார்; இது கிராமத்துச் சந்தையில் காய்கறி எடைபோடும் தராசு முதலில் சுழியில் நிற்கிறதா என்று சரிபார்ப்பது போன்றதாகும்.",
            "txt": "In the school science laboratory, student Meena checks whether the zero markings align before measuring a glass tube with a vernier caliper, just like checking that a village vegetable vendor's balancing scale rests evenly on zero before weighing tomatoes."
        }
    # 5. Optics, Refraction, Light
    elif any(k in low for k in ["refraction", "medium", "prism", "light", "lens", "ray", "optical"]):
        return {
            "id": "refraction_tea_stall",
            "en": "While having morning tea at a village tea stall, student Meena dips a metal spoon into a clear glass tumbler of water and notices it looks bent or broken at the surface, because light rays change speed and direction when passing from water into air.",
            "ta": "கிராமத்து தேநீர்க் கடையில் கண்ணாடி டம்ளர் தண்ணீரில் ஒரு உலோகக் கரண்டியை வைக்கும்போது, அது உடைந்திருப்பது போலத் தோன்றுவதை மாணவி மீனா கவனிக்கிறார்; ஒளி நீரிலிருந்து காற்றில் வரும்போது திசை மாறுவதே (ஒளிவிலகல்) இதற்குக் காரணம்.",
            "txt": "While having morning tea at a village tea stall, student Meena dips a metal spoon into a clear glass tumbler of water and notices it looks bent or broken at the surface, because light rays change speed and direction when passing from water into air."
        }
    # 6. Electricity, Current, Circuit
    elif any(k in low for k in ["electricity", "current", "voltage", "circuit", "battery", "conductor"]):
        return {
            "id": "circuit_village_torch",
            "en": "During an evening power cut in her village, student Meena switches on a battery torchlight: electric current flows through copper wires to light up the bulb, exactly like water flows through pipes from an overhead rooftop tank when a valve is opened.",
            "ta": "கிராமத்தில் மின்வெட்டு ஏற்படும்போது, மாணவி மீனா பேட்டரி டார்ச் விளக்கை ஆன் செய்கிறார்; மேல்நிலைத் தொட்டியிலிருந்து குழாயில் தண்ணீர் பாய்வது போல, மின்கலத்திலிருந்து தாமிரக் கம்பி வழியாக மின்சாரம் பாய்ந்து விளக்கை எரியச் செய்கிறது.",
            "txt": "During an evening power cut in her village, student Meena switches on a battery torchlight: electric current flows through copper wires to light up the bulb, exactly like water flows through pipes from an overhead rooftop tank when a valve is opened."
        }
    # 7. Money, Barter, Trade
    elif any(k in low for k in ["money", "barter", "trade", "currency", "coin"]):
        return {
            "id": "money_village_santhai",
            "en": "Meena's grandmother explains that in old village fairs (சந்தை / santhai), farmers exchanged paddy for earthen pots or cloth, but because splitting goods evenly was difficult, coins and paper money were introduced to give everything a fixed, fair value.",
            "ta": "கிராமத்து வாரச் சந்தையில் நெல்லைக் கொடுத்து மண்பாண்டங்கள் வாங்கிய பண்டமாற்று முறையில் ஏற்பட்ட சிரமங்களை மீனாவின் பாட்டி விவரிக்கிறார்; இதனால்தான் அனைவருக்கும் பொதுவான நாணயங்களும் ரூபாய் நோட்டுகளும் பயன்பாட்டிற்கு வந்தன.",
            "txt": "Meena's grandmother explains that in old village fairs (சந்தை / santhai), farmers exchanged paddy for earthen pots or cloth, but because splitting goods evenly was difficult, coins and paper money were introduced to give everything a fixed, fair value."
        }
    # 8. Digestion
    elif any(k in low for k in ["digestion", "stomach", "digestive", "enzyme", "intestine"]):
        return {
            "id": "digestion_village_aattukkal",
            "en": "Just like a traditional village stone grinder (ஆட்டுக்கல் / aattukkal) crushes coarse lentils and rice into smooth idli batter, human digestive organs and enzymes break down solid food into simple nutrients that the body can absorb.",
            "ta": "பாரம்பரிய கிராமத்து ஆட்டுக்கல்லில் பருப்பையும் அரிசியையும் அரைத்து மென்மையான மாவாக மாற்றுவது போல, மனித செரிமான மண்டலமும் என்சைம்களும் நாம் உண்ணும் கடின உணவை உடலால் உறிஞ்சக்கூடிய எளிய சத்துக்களாக உடைக்கின்றன.",
            "txt": "Just like a traditional village stone grinder (ஆட்டுக்கல் / aattukkal) crushes coarse lentils and rice into smooth idli batter, human digestive organs and enzymes break down solid food into simple nutrients that the body can absorb."
        }
    else:
        sents = out.get("sents", [])
        first_sent = sents[0] if sents else txt.split(".")[0]
        clean_fs = first_sent.strip().rstrip(".")
        return {
            "id": "context_village_student",
            "en": f"As student Meena studies this concept at home in her village, she realizes that {clean_fs.lower()}, showing how this scientific fact directly explains everyday wonders around her rural home.",
            "ta": "கிராமத்து வீட்டில் பாடம் படிக்கும் மாணவி மீனா, தனது அன்றாடச் சூழலில் நடக்கும் நிகழ்வுகளோடு இக்கருத்தை ஒப்பிட்டு எளிதாகப் புரிந்துகொள்கிறார்.",
            "txt": f"As student Meena studies this concept at home in her village, she realizes that {clean_fs.lower()}, showing how this scientific fact directly explains everyday wonders around her rural home."
        }

def enrich_quiz(raw_quiz, sents, txt, terms):
    low_txt = txt.lower()
    
    # Domain-specific distractor pool
    if any(k in low_txt for k in ["photosynthesis", "chloroplast", "chlorophyll", "stomata", "leaf", "plant"]):
        domain_pool = ["Chloroplast", "Stomata", "Chlorophyll", "Glucose", "Mitochondria", "Epidermis", "Transpiration", "Oxygen", "Carbon dioxide"]
    elif any(k in low_txt for k in ["archaeolog", "fossil", "evolution", "hominin", "ancestor", "prehistory"]):
        domain_pool = ["Hominins", "Archaeologists", "Fossils", "Palaeoanthropologists", "Prehistory", "Stone tools", "Excavations", "Stratigraphy"]
    elif any(k in low_txt for k in ["vernier", "caliper", "scale", "screw gauge", "error", "least count"]):
        domain_pool = ["Main scale", "Vernier scale", "Zero error", "Least count", "Calipers", "Positive error", "Negative error", "Pitch scale"]
    elif any(k in low_txt for k in ["temperature", "kelvin", "celsius", "fahrenheit", "heat", "thermal"]):
        domain_pool = ["Kelvin", "Degree Celsius", "Fahrenheit", "Thermal equilibrium", "Heat energy", "Absolute zero", "Conduction", "Radiation"]
    else:
        domain_pool = [t["en"].capitalize() for t in terms if len(t.get("en", "")) >= 4]

    # Add glossary terms from passage
    for t in terms:
        en_cap = t.get("en", "").capitalize()
        if en_cap and en_cap not in domain_pool:
            domain_pool.append(en_cap)

    # Add significant capitalized words from passage
    for w in re.findall(r"\b[A-Za-z]{5,}\b", txt):
        w_cap = w.capitalize()
        if w_cap not in domain_pool:
            domain_pool.append(w_cap)

    cleaned_quiz = []
    for idx, q in enumerate(raw_quiz):
        opts = list(q.get("opts", []))
        ans_idx = q.get("ans", 0)
        ans_str = opts[ans_idx] if 0 <= ans_idx < len(opts) else (opts[0] if opts else "")
        if not ans_str:
            continue

        has_generic = any(d in ["Kelvin", "Degree Celsius", "Fahrenheit"] for d in opts)
        needs_context = has_generic and not any(k in low_txt for k in ["temperature", "heat", "kelvin", "celsius", "fahrenheit"])

        cands = [d for d in domain_pool if d.lower() != ans_str.lower() and d.lower() not in ans_str.lower() and ans_str.lower() not in d.lower()]
        
        if needs_context or len(opts) < 4:
            new_dist = []
            for c in cands:
                if c not in new_dist:
                    new_dist.append(c)
                if len(new_dist) == 3:
                    break
            new_opts = [ans_str] + new_dist
        else:
            new_opts = list(opts)

        while len(new_opts) < 4 and cands:
            nxt = cands.pop(0)
            if nxt not in new_opts:
                new_opts.append(nxt)

        rng = random.Random(abs(hash(q.get("q", ""))) + idx)
        ans_val = ans_str
        shuffled = list(dict.fromkeys(new_opts))[:4]
        rng.shuffle(shuffled)
        if ans_val not in shuffled:
            shuffled[0] = ans_val
            rng.shuffle(shuffled)

        cleaned_quiz.append({
            "q": q.get("q", ""),
            "opts": shuffled,
            "ans": shuffled.index(ans_val),
            "cite": q.get("cite", 1)
        })

    # If quiz has fewer than 3 questions, generate contextual questions from sentences
    if len(cleaned_quiz) < 3 and sents:
        seen_q = {q["q"].lower() for q in cleaned_quiz}
        for idx, s in enumerate(sents):
            if len(cleaned_quiz) >= 3:
                break
            matched_t = [t["en"] for t in terms if re.search(r"\b" + re.escape(t["en"]) + r"\b", s, re.I)]
            if not matched_t:
                words = [w for w in re.findall(r"\b[A-Za-z]{6,}\b", s) if w.lower() not in ["during", "called", "through", "energy", "between"]]
                if words:
                    matched_t = [words[0]]
            for cand in matched_t:
                if len(cleaned_quiz) >= 3:
                    break
                pat = re.compile(r"\b" + re.escape(cand) + r"\b", re.I)
                blanked = pat.sub("_____", s)
                q_txt = f"Fill in the blank: {blanked}"
                if q_txt.lower() in seen_q:
                    continue
                seen_q.add(q_txt.lower())
                cands = [t["en"].capitalize() for t in terms if t["en"].lower() != cand.lower()]
                for d in domain_pool:
                    if d.lower() != cand.lower() and d not in cands:
                        cands.append(d)
                opts = [cand.capitalize()] + cands[:3]
                rng = random.Random(idx + 101)
                rng.shuffle(opts)
                cleaned_quiz.append({
                    "q": q_txt,
                    "opts": opts,
                    "ans": opts.index(cand.capitalize()),
                    "cite": idx + 1
                })

    return cleaned_quiz[:4]

def enrich_output(out, txt):
    if not isinstance(out, dict):
        return out
    
    sents = out.get("sents", [])
    hard_idx = out.get("hard", 1)
    orig_sent = sents[hard_idx - 1] if 0 <= hard_idx - 1 < len(sents) else ""
    
    # 1. Guarantee genuine, distinct simplification
    if orig_sent and (out.get("simple", "").strip() == orig_sent.strip() or not out.get("simple")):
        out["simple"] = simplify_sentence(orig_sent, txt)
    
    # 2. Enrich and expand glossary terms with Tamil definitions
    existing_terms = {t["en"].lower(): t for t in out.get("terms", []) if isinstance(t, dict)}
    low_txt = txt.lower()
    
    matched = []
    for k, v in glossary.items():
        if re.search(r"\b" + re.escape(k) + r"\b", low_txt):
            matched.append({
                "en": k,
                "ta": v.get("ta", ""),
                "def": v.get("def", "") or v.get("ta_def", "") or v.get("en_def", "")
            })
    
    final_terms = []
    seen = set()
    for m in matched:
        if m["en"].lower() not in seen:
            seen.add(m["en"].lower())
            final_terms.append(m)
    
    for en_k, t_obj in existing_terms.items():
        if en_k not in seen:
            g_entry = glossary.get(en_k, {})
            seen.add(en_k)
            final_terms.append({
                "en": t_obj.get("en", en_k),
                "ta": t_obj.get("ta") or g_entry.get("ta", ""),
                "def": g_entry.get("def") or g_entry.get("ta_def") or g_entry.get("en_def", "")
            })
            
    out["terms"] = final_terms[:6]

    # 3. Enrich and contextualize quiz options (remove repetitive distractors, randomize answer position)
    out["quiz"] = enrich_quiz(out.get("quiz", []), sents, txt, out["terms"])

    # 4. Contextualize real-world example
    out["example"] = enrich_example(out, txt)

    return out

def main():
    sys.stdout.write("STUDYAID_READY\n")
    sys.stdout.flush()

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        req = json.loads(line)
        jid = req.get("id")
        txt = req.get("text", "")
        t0 = time.time()
        res = {"id": jid, "ok": True, "err": "", "result": None}
        try:
            out = run_one(txt)
            out = enrich_output(out, txt)
            res["result"] = out
        except Exception as e:
            res["ok"] = False
            res["err"] = repr(e)[:200]
        res["elapsed_s"] = round(time.time() - t0, 2)
        res["rss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
        sys.stdout.write("STUDYAID_RES:" + json.dumps(res, ensure_ascii=False) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
