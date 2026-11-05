import os
import sys
import time
import json
import psutil
from studyaid.backend import ETBackend
from studyaid.gloss import load_gl
from studyaid.pipeline import run_pipeline
from studyaid.telem import collect_telem
from studyaid.render import render_all

def main():
    m_pte = "models/llama1b/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte"
    m_tok = "models/llama1b/tokenizer.model"
    gl_p = "data/tamil_glossary.json"
    gl = load_gl(gl_p) if os.path.exists(gl_p) else {}

    s_files = [
        "samples/optics.txt",
        "samples/photosynthesis.txt",
        "samples/circuits.txt",
        "samples/digestion.txt",
        "samples/sound.txt",
    ]

    t0 = time.perf_counter()
    bk = ETBackend(m_pte, m_tok)
    ld_dt = time.perf_counter() - t0

    rows = []
    tot_quiz = 0
    sup_quiz = 0
    retries = 0

    for fp in s_files:
        with open(fp, "r", encoding="utf-8") as f:
            txt = f.read().strip()
        w_cnt = len(txt.split())

        t_st = time.perf_counter()
        res = run_pipeline(txt, bk, gl, max_new=480, two_pass=True)
        inf_dt = time.perf_counter() - t_st

        m_info = psutil.Process().memory_info()
        rss_mb = round(m_info.rss / (1024 * 1024), 2)
        n_tok = res["tok_cnt"]
        tps = round(n_tok / inf_dt, 2) if inf_dt > 0 else 0.0

        q_items = res.get("quiz", [])
        q_cnt = len(q_items)
        s_cnt = sum(1 for q in q_items if q.get("status", "").lower() == "supported")
        tot_quiz += q_cnt
        sup_quiz += s_cnt

        had_ret = (res.get("parsed", {}).get("missing") == []) and (n_tok > 350)
        if had_ret:
            retries += 1

        telem_data = collect_telem(
            m_name=bk.name,
            pte_path=m_pte,
            tok_cnt=n_tok,
            inf_time=inf_dt,
            is_mock=False
        )
        rep, txt_p, j_p = render_all(res, telem_data, out_dir="outputs")

        row = {
            "file": os.path.basename(fp),
            "words": w_cnt,
            "inf_time": round(inf_dt, 2),
            "rss_mb": rss_mb,
            "tokens": n_tok,
            "tps": tps,
            "quiz_cnt": q_cnt,
            "quiz_sup": s_cnt,
            "saved_txt": txt_p,
            "saved_json": j_p
        }
        rows.append(row)
        print(f"Done {row['file']}: time={row['inf_time']}s, rss={row['rss_mb']}MB, tok={row['tokens']}, tps={row['tps']}, quiz={s_cnt}/{q_cnt}")

    b_res = {
        "load_time": round(ld_dt, 3),
        "rows": rows,
        "tot_runs": len(rows),
        "avg_inf_time": round(sum(r["inf_time"] for r in rows) / len(rows), 2),
        "min_inf_time": min(r["inf_time"] for r in rows),
        "max_inf_time": max(r["inf_time"] for r in rows),
        "avg_rss_mb": round(sum(r["rss_mb"] for r in rows) / len(rows), 2),
        "min_rss_mb": min(r["rss_mb"] for r in rows),
        "max_rss_mb": max(r["rss_mb"] for r in rows),
        "avg_tps": round(sum(r["tps"] for r in rows) / len(rows), 2),
        "tot_quiz": tot_quiz,
        "sup_quiz": sup_quiz,
        "sup_rate_pct": round(100.0 * sup_quiz / tot_quiz, 1) if tot_quiz > 0 else 0.0,
        "retries": retries
    }

    out_p = "outputs/benchmark_summary.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(b_res, f, indent=2)

    print("\n=== BENCHMARK SUMMARY ===")
    print(json.dumps(b_res, indent=2))

if __name__ == "__main__":
    main()