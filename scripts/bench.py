import os
import sys
import json
import time
import argparse
import tomllib
from studyaid.backend import ETBackend, MockBackend
from studyaid.gloss import load_gl
from studyaid.pipeline import run_pipeline
from studyaid.telem import collect_telem, get_net_state, get_peak_rss_mib
from studyaid.render import build_report

PASSAGES = [
    "optics",
    "photosynthesis",
    "circuits",
    "digestion",
    "sound",
    "optics_long"
]

def load_cfg(cfg_path):
    if os.path.exists(cfg_path):
        with open(cfg_path, "rb") as f:
            return tomllib.load(f)
    return {}

def fmt_stat(vals, decimals=2):
    if not vals:
        return "0"
    m = sum(vals) / len(vals)
    lo = min(vals)
    hi = max(vals)
    if decimals == 0:
        return f"{m:.0f} ({lo:.0f}-{hi:.0f})"
    elif decimals == 1:
        return f"{m:.1f} ({lo:.1f}-{hi:.1f})"
    return f"{m:.2f} ({lo:.2f}-{hi:.2f})"

def run_bench(args):
    cfg = load_cfg(args.config)
    m_cfg = cfg.get("model", {})
    r_cfg = cfg.get("runtime", {})

    if args.require_offline:
        net = get_net_state()
        if not net.get("is_offline"):
            active = [f"{it['name']}={it['state']}" for it in net.get("ifaces", []) if it["name"] != "lo" and it["state"] != "DOWN"]
            act_str = ", ".join(active) if active else "none"
            def_str = "YES" if net.get("has_def_route") else "NO"
            sys.exit(f"Error: system is ONLINE (active interfaces: {act_str}, default route: {def_str}). Offline required by --require-offline.")

    pte_p = args.pte or m_cfg.get("pte", "")
    tok_p = args.tokenizer or m_cfg.get("tokenizer", "")
    m_name = m_cfg.get("name", "Llama-3.2-1B-Instruct")
    is_mock = args.mock or r_cfg.get("mock", False)
    gl_p = args.glossary or "data/tamil_glossary.json"
    gl = load_gl(gl_p) if os.path.exists(gl_p) else {}

    p1_max = int(m_cfg.get("max_new_pass1", 320))
    p2_max = int(m_cfg.get("max_new_pass2", 220))

    os.makedirs(args.out_dir, exist_ok=True)

    t_load_0 = time.perf_counter()
    if is_mock or not pte_p:
        bk = MockBackend()
    else:
        bk = ETBackend(pte_p, tok_p)
    load_time = round(time.perf_counter() - t_load_0, 3)

    raw_runs = []
    by_passage = {p: [] for p in PASSAGES}

    for p_name in PASSAGES:
        p_path = f"samples/{p_name}.txt"
        if not os.path.exists(p_path):
            print(f"Skipping missing passage file: {p_path}")
            continue
        with open(p_path, "r", encoding="utf-8") as f:
            p_txt = f.read()
        w_cnt = len(p_txt.split())

        for r_idx in range(1, args.runs + 1):
            print(f"Running {p_name} (run {r_idx}/{args.runs})...", flush=True)
            t0 = time.perf_counter()
            pipe_res = run_pipeline(
                p_txt,
                bk,
                gl,
                max_new_p1=p1_max,
                max_new_p2=p2_max,
                two_pass=True
            )
            inf_sec = round(time.perf_counter() - t0, 3)

            telem_res = collect_telem(
                m_name=m_name,
                pte_path=pte_p,
                tok_cnt=pipe_res["tok_cnt"],
                inf_time=inf_sec,
                is_mock=getattr(bk, "is_mock", False)
            )

            rep_txt = build_report(pipe_res, telem_res)
            
            run_txt_p = os.path.join(args.out_dir, f"{p_name}_{r_idx}.txt")
            run_json_p = os.path.join(args.out_dir, f"{p_name}_{r_idx}.json")
            with open(run_txt_p, "w", encoding="utf-8") as f:
                f.write(rep_txt)

            retries_cnt = (1 if pipe_res["p1_info"]["retried"] else 0) + (1 if pipe_res["p2_info"]["retried"] else 0)
            
            record = {
                "passage": p_name,
                "run": r_idx,
                "words": w_cnt,
                "load_time_sec": load_time,
                "p1_sec": pipe_res["p1_info"]["seconds"],
                "p1_tokens": pipe_res["p1_info"]["tokens"],
                "p1_retried": pipe_res["p1_info"]["retried"],
                "p1_retry_reason": pipe_res["p1_info"]["reason"],
                "p2_sec": pipe_res["p2_info"]["seconds"],
                "p2_tokens": pipe_res["p2_info"]["tokens"],
                "p2_retried": pipe_res["p2_info"]["retried"],
                "p2_retry_reason": pipe_res["p2_info"]["reason"],
                "inf_time_sec": inf_sec,
                "tokens": pipe_res["tok_cnt"],
                "tok_per_sec": telem_res["tok_per_sec"],
                "peak_rss_mib": telem_res["peak_rss_mib"],
                "retries": retries_cnt,
                "guards": pipe_res["guards"],
                "offline_status": "OFFLINE" if telem_res["net"]["is_offline"] else "ONLINE",
                "telemetry": telem_res,
                "pipeline": pipe_res
            }

            with open(run_json_p, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, ensure_ascii=False)

            raw_runs.append(record)
            by_passage[p_name].append(record)

    summary_rows = []
    for p_name, runs in by_passage.items():
        if not runs:
            continue
        w_cnt = runs[0]["words"]
        times = [r["inf_time_sec"] for r in runs]
        toks = [r["tokens"] for r in runs]
        tps = [r["tok_per_sec"] for r in runs]
        rss = [r["peak_rss_mib"] for r in runs]
        retries = [r["retries"] for r in runs]
        
        sup_cnts = [r["guards"]["quiz_supported_cnt"] for r in runs]
        tot_quiz = [r["guards"]["quiz_total_cnt"] for r in runs]
        shorter_cnts = [1 if r["guards"]["rewrite_shorter"] else 0 for r in runs]
        vil_cnts = [1 if r["guards"]["village_relevant"] else 0 for r in runs]
        exp_cnts = [r["guards"]["words_explained_cnt"] for r in runs]
        cand_cnts = [r["guards"]["words_cand_cnt"] for r in runs]

        summary_rows.append({
            "passage": p_name,
            "words": w_cnt,
            "runs": len(runs),
            "inf_time": fmt_stat(times, 2),
            "inf_time_mean": round(sum(times) / len(times), 2),
            "tokens": fmt_stat(toks, 0),
            "tokens_mean": round(sum(toks) / len(toks), 0),
            "tps": fmt_stat(tps, 2),
            "tps_mean": round(sum(tps) / len(tps), 2),
            "rss": fmt_stat(rss, 1),
            "rss_mean": round(sum(rss) / len(rss), 1),
            "retries": fmt_stat(retries, 1),
            "retries_mean": round(sum(retries) / len(retries), 1),
            "quiz_sup": f"{sum(sup_cnts)}/{sum(tot_quiz)}",
            "shorter": f"{sum(shorter_cnts)}/{len(runs)}",
            "village_rel": f"{sum(vil_cnts)}/{len(runs)}",
            "words_exp": f"{sum(exp_cnts)}/{sum(cand_cnts)}"
        })

    all_times = [r["inf_time_sec"] for r in raw_runs]
    all_toks = [r["tokens"] for r in raw_runs]
    all_tps = [r["tok_per_sec"] for r in raw_runs]
    all_rss = [r["peak_rss_mib"] for r in raw_runs]
    all_retries = [r["retries"] for r in raw_runs]
    all_sup = sum(r["guards"]["quiz_supported_cnt"] for r in raw_runs)
    all_quiz = sum(r["guards"]["quiz_total_cnt"] for r in raw_runs)
    all_shorter = sum(1 if r["guards"]["rewrite_shorter"] else 0 for r in raw_runs)
    all_vil = sum(1 if r["guards"]["village_relevant"] else 0 for r in raw_runs)
    all_exp = sum(r["guards"]["words_explained_cnt"] for r in raw_runs)
    all_cands = sum(r["guards"]["words_cand_cnt"] for r in raw_runs)

    overall = {
        "passage": "Overall Mean",
        "words": round(sum(r["words"] for r in summary_rows) / len(summary_rows), 0) if summary_rows else 0,
        "runs": len(raw_runs),
        "inf_time": fmt_stat(all_times, 2),
        "tokens": fmt_stat(all_toks, 0),
        "tps": fmt_stat(all_tps, 2),
        "rss": fmt_stat(all_rss, 1),
        "retries": fmt_stat(all_retries, 1),
        "quiz_sup": f"{all_sup}/{all_quiz}",
        "shorter": f"{all_shorter}/{len(raw_runs)}",
        "village_rel": f"{all_vil}/{len(raw_runs)}",
        "words_exp": f"{all_exp}/{all_cands}"
    }

    full_bench = {
        "meta": {
            "model": m_name,
            "pte_path": pte_p,
            "backend": "mock" if is_mock else "executorch",
            "runs_per_passage": args.runs,
            "offline_status": "OFFLINE" if (raw_runs and all(r["offline_status"] == "OFFLINE" for r in raw_runs)) else "ONLINE"
        },
        "summary": summary_rows,
        "overall": overall
    }

    with open(args.summary_json, "w", encoding="utf-8") as f:
        json.dump(full_bench, f, indent=2, ensure_ascii=False)

    md_lines = [
        "# StudyAid Benchmark Results",
        "",
        f"**Model:** {m_name}  ",
        f"**Backend:** {'Mock' if is_mock else 'Real ExecuTorch'}  ",
        f"**Runs per passage:** {args.runs}  ",
        f"**Status:** {full_bench['meta']['offline_status']}  ",
        "",
        "| Passage | Words | Latency (s) | Tokens | Tokens/s | Peak RSS (MiB) | Retries | Quiz Sup | Shorter | Village | Words Exp |",
        "|---|---|---|---|---|---|---|---|---|---|---|"
    ]
    for row in summary_rows:
        md_lines.append(
            f"| {row['passage']} | {row['words']} | {row['inf_time']} | {row['tokens']} | {row['tps']} | {row['rss']} | {row['retries']} | {row['quiz_sup']} | {row['shorter']} | {row['village_rel']} | {row['words_exp']} |"
        )
    md_lines.append(
        f"| **{overall['passage']}** | {overall['words']} | **{overall['inf_time']}** | **{overall['tokens']}** | **{overall['tps']}** | **{overall['rss']}** | **{overall['retries']}** | **{overall['quiz_sup']}** | **{overall['shorter']}** | **{overall['village_rel']}** | **{overall['words_exp']}** |"
    )
    md_lines.append("")

    with open(args.summary_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"\n[Benchmark complete]: Saved {args.summary_json} and {args.summary_md}")

def main():
    p = argparse.ArgumentParser(description="StudyAid Benchmark Runner")
    p.add_argument("--config", default="config.toml")
    p.add_argument("--pte", default=None)
    p.add_argument("--tokenizer", default=None)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--glossary", default="data/tamil_glossary.json")
    p.add_argument("--out-dir", default="evidence/runs")
    p.add_argument("--summary-json", default="evidence/benchmark.json")
    p.add_argument("--summary-md", default="evidence/benchmark.md")
    p.add_argument("--require-offline", action="store_true", default=False)
    p.add_argument("--mock", action="store_true", default=False)

    args = p.parse_args()
    run_bench(args)

if __name__ == "__main__":
    main()
