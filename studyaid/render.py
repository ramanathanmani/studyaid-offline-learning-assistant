import os
import json
from datetime import datetime

def fmt_table(comp):
    if not comp:
        return "N/A"
    o = comp["orig"]
    s = comp["simp"]
    d = comp["diff"]
    w_chg = f"{d['w_chg']:+.1f}%"
    l_chg = f"{d['l_chg']:+.1f}%"
    avg_chg = f"{d['avg_chg']:+.1f}%"
    lines = [
        f"{'Metric':<22} {'Original':<12} {'Simplified':<12} {'Change (%)':<10}",
        f"{'Words':<22} {o['w_cnt']:<12} {s['w_cnt']:<12} {w_chg:<10}",
        f"{'Letters':<22} {o['l_cnt']:<12} {s['l_cnt']:<12} {l_chg:<10}",
        f"{'Avg letters/word':<22} {o['avg_l']:<12.2f} {s['avg_l']:<12.2f} {avg_chg:<10}"
    ]
    return "\n".join(lines)

def build_report(pipe_res, telem_res):
    buf = []
    if pipe_res.get("is_mock"):
        buf.append("[MOCK BACKEND: not a real model run]\n")

    buf.append("=== NUMBERED PASSAGE / பாடப்பகுதி ===")
    for sid, stxt in pipe_res["s_list"]:
        buf.append(f"[{sid}] {stxt}")
    buf.append("")

    buf.append("=== HARDEST SENTENCE BEFORE / AFTER / கடின வாக்கியம் (முன் / பின்) ===")
    hs = pipe_res["hard_s"]
    parsed = pipe_res["parsed"]
    buf.append(f"Original ([{hs['id']}]): {hs['text']}")
    if parsed.get("no_simpler"):
        buf.append(f"Simplified:   {parsed['simple']} (no simpler rewrite produced)")
    else:
        buf.append(f"Simplified:   {parsed['simple'] or 'N/A'}")
    buf.append("\nReadability Metrics:")
    buf.append(fmt_table(pipe_res["readab"]))
    buf.append("")

    buf.append("=== SIMPLE SUMMARY / எளிய சுருக்கம் ===")
    buf.append(parsed["summary"] or "N/A")
    buf.append("")

    buf.append("=== VILLAGE LIFE EXAMPLE / கிராமப்புற உதாரணம் ===")
    buf.append(parsed["village"] or "N/A")
    buf.append("")

    buf.append("=== HARD WORDS & TAMIL GLOSSARY / கடின சொற்கள் & தமிழாக்கம் ===")
    words = pipe_res.get("words", [])
    if words:
        for it in words:
            gl = it.get("gl")
            if gl:
                tag = "[verified]" if gl.get("verified") else "[unverified]"
                buf.append(f"- {it['word']}: {it['meaning']} -> {gl['ta']} ({gl['translit']}) {tag}")
            else:
                buf.append(f"- {it['word']}: {it['meaning']} (English only)")
    else:
        buf.append("No hard words parsed.")
    buf.append("")

    buf.append("=== QUIZ QUESTIONS / வினாடி வினா ===")
    quiz = pipe_res.get("quiz", [])
    if quiz:
        for idx, q in enumerate(quiz, 1):
            buf.append(f"[Q{idx}] {q['q']}")
            buf.append(f"     Answer: {q['a']}")
            buf.append(f"     Citation: {q['c']}")
            sh_str = ", ".join(q["shared"]) if q["shared"] else "none"
            if q["status"] == "SUPPORTED (exact term)":
                buf.append(f"     Support: SUPPORTED (exact term)")
            elif q["status"].upper() == "SUPPORTED":
                buf.append(f"     Support: SUPPORTED (shared: {sh_str})")
            else:
                sug_str = f", suggested citation: {q['suggested']}" if q.get("suggested") else ""
                buf.append(f"     Support: FLAGGED (shared: {sh_str}{sug_str})")
    else:
        buf.append("No quiz items available.")
    buf.append("")

    buf.append("=== JUDGE PROOF TELEMETRY ===")
    h = telem_res["host"]
    net = telem_res["net"]
    buf.append(h["host_label"])
    buf.append(f"OS: {h['os']}")
    buf.append(f"CPU: {h['cpu_model']}")
    buf.append(f"Cores: {h['cores']}")
    buf.append(f"Total RAM: {h['ram_gb']} GB")
    
    iface_str = ", ".join(f"{it['name']}={it['state']}" for it in net.get("ifaces", []))
    buf.append(f"Network interfaces: {iface_str or 'none detected'}")
    buf.append(f"Default route active: {'YES' if net.get('has_def_route') else 'NO'}")
    buf.append(f"Offline status: {'OFFLINE' if net.get('is_offline') else 'ONLINE'}")
    
    buf.append(f"Model name: {telem_res['model_name']}")
    if telem_res.get("pte_size_mib"):
        buf.append(f"PTE size: {telem_res['pte_size_mib']} MiB ({telem_res.get('pte_size_bytes', 0)} bytes)")
    else:
        buf.append("PTE size: N/A (mock run)")
    buf.append(f"Peak RSS: {telem_res['peak_rss_mib']} MiB")
    buf.append(f"Inference time: {telem_res['inf_time_sec']} s")
    buf.append(f"Tokens generated: {telem_res['tok_cnt']}")
    buf.append(f"Tokens/sec: {telem_res['tok_per_sec']}")
    mode_str = "[MOCK BACKEND: not a real model run]" if telem_res.get("is_mock") else "[REAL EXECUTORCH RUN]"
    buf.append(f"Execution mode: {mode_str}")

    return "\n".join(buf)

def save_outputs(pipe_res, telem_res, rep_txt, out_dir="outputs"):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_path = os.path.join(out_dir, f"run_{ts}.txt")
    json_path = os.path.join(out_dir, f"run_{ts}.json")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(rep_txt)

    payload = {
        "timestamp": ts,
        "pipeline": pipe_res,
        "telemetry": telem_res
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return txt_path, json_path

def render_all(pipe_res, telem_res, out_dir="outputs"):
    rep_txt = build_report(pipe_res, telem_res)
    txt_p, json_p = save_outputs(pipe_res, telem_res, rep_txt, out_dir)
    return rep_txt, txt_p, json_p
