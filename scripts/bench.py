import os
import sys
import json
import time
import argparse
import subprocess
import resource
import platform
import tomllib
import psutil
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

def compute_benchmark_stats(raw_runs, m_name="", pte_p="", is_mock=False, runs_per_p=3):
    by_p = {}
    for r in raw_runs:
        by_p.setdefault(r["passage"], []).append(r)

    summary_rows = []
    p_words = []
    for p_name in PASSAGES:
        runs = by_p.get(p_name, [])
        if not runs:
            continue
        w_cnt = runs[0]["words"]
        p_words.append(w_cnt)
        times = [r["inf_time_sec"] for r in runs]
        toks = [r["tokens"] for r in runs]
        tps = [r["tok_per_sec"] for r in runs]
        rss = [r["peak_rss_mib"] for r in runs]
        base_rss = [r.get("baseline_rss_mib", 0.0) for r in runs]
        retries = [r["retries"] for r in runs]
        
        quiz_cnts = [r.get("quiz_count", len(r["pipeline"]["quiz"])) for r in runs]
        sup_cnts = [r["guards"]["quiz_supported_cnt"] for r in runs]
        tot_quiz = [r["guards"]["quiz_total_cnt"] for r in runs]
        sum_ok = [1 if r.get("summary_ok", True) else 0 for r in runs]
        shorter_cnts = [1 if r["guards"]["rewrite_shorter"] else 0 for r in runs]
        vil_cnts = [1 if r["guards"].get("village_format_ok", r["guards"].get("village_relevant", True)) else 0 for r in runs]
        exp_cnts = [r["guards"]["words_explained_cnt"] for r in runs]
        cand_cnts = [r["guards"]["words_cand_cnt"] for r in runs]
        model_cites = [r["guards"].get("quiz_model_cite_cnt", 0) for r in runs]

        reasons_list = [r.get("p1_retry_reason", "") for r in runs if r.get("p1_retried")]
        reasons_list += [r.get("p2_retry_reason", "") for r in runs if r.get("p2_retried")]
        clean_reasons = sorted(list(set(r.strip() for r in reasons_list if r.strip() and r.strip() != "none")))
        r_str = "; ".join(clean_reasons) if clean_reasons else "none"

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
            "base_rss": fmt_stat(base_rss, 1),
            "base_rss_mean": round(sum(base_rss) / len(base_rss), 1),
            "retries": fmt_stat(retries, 1),
            "retries_mean": round(sum(retries) / len(retries), 1),
            "reasons": r_str,
            "quiz_items": round(sum(quiz_cnts) / len(runs), 1),
            "quiz_model_cite": f"{sum(model_cites)}/{sum(tot_quiz)}",
            "quiz_sup": f"{sum(sup_cnts)}/{sum(tot_quiz)}",
            "summary_ok": f"{sum(sum_ok)}/{len(runs)}",
            "shorter": f"{sum(shorter_cnts)}/{len(runs)}",
            "village_fmt": f"{sum(vil_cnts)}/{len(runs)}",
            "village_rel": f"{sum(vil_cnts)}/{len(runs)}",
            "words_exp": f"{sum(exp_cnts)}/{sum(cand_cnts)}",
            "offline_status": "OFFLINE" if all(r.get("offline_status") == "OFFLINE" for r in runs) else "ONLINE"
        })

    all_times = [r["inf_time_sec"] for r in raw_runs]
    all_toks = [r["tokens"] for r in raw_runs]
    all_tps = [r["tok_per_sec"] for r in raw_runs]
    all_rss = [r["peak_rss_mib"] for r in raw_runs]
    all_base = [r.get("baseline_rss_mib", 0.0) for r in raw_runs]
    all_retries = [r["retries"] for r in raw_runs]
    all_quiz_cnts = [r.get("quiz_count", len(r["pipeline"]["quiz"])) for r in raw_runs]
    all_model_cites = [r["guards"].get("quiz_model_cite_cnt", 0) for r in raw_runs]
    all_sup = sum(r["guards"]["quiz_supported_cnt"] for r in raw_runs)
    all_quiz = sum(r["guards"]["quiz_total_cnt"] for r in raw_runs)
    all_sum_ok = sum(1 if r.get("summary_ok", True) else 0 for r in raw_runs)
    all_shorter = sum(1 if r["guards"]["rewrite_shorter"] else 0 for r in raw_runs)
    all_vil = sum(1 if r["guards"].get("village_format_ok", r["guards"].get("village_relevant", True)) else 0 for r in raw_runs)
    all_exp = sum(r["guards"]["words_explained_cnt"] for r in raw_runs)
    all_cands = sum(r["guards"]["words_cand_cnt"] for r in raw_runs)

    all_reasons = []
    for r in raw_runs:
        if r.get("p1_retried") and r.get("p1_retry_reason"):
            all_reasons.append(r["p1_retry_reason"].strip())
        if r.get("p2_retried") and r.get("p2_retry_reason"):
            all_reasons.append(r["p2_retry_reason"].strip())
    clean_all_reasons = sorted(list(set(r for r in all_reasons if r and r != "none")))
    all_r_str = "; ".join(clean_all_reasons) if clean_all_reasons else "none"

    overall_mean_words = round(sum(p_words) / len(p_words), 1) if p_words else 0.0

    overall = {
        "passage": "Overall Mean",
        "words": overall_mean_words,
        "runs": len(raw_runs),
        "inf_time": fmt_stat(all_times, 2),
        "tokens": fmt_stat(all_toks, 0),
        "tps": fmt_stat(all_tps, 2),
        "rss": fmt_stat(all_rss, 1),
        "base_rss": fmt_stat(all_base, 1),
        "retries": fmt_stat(all_retries, 1),
        "reasons": "mean count across passages",
        "quiz_items": round(sum(all_quiz_cnts) / len(raw_runs), 1) if raw_runs else 0,
        "quiz_model_cite": f"{sum(all_model_cites)}/{all_quiz}",
        "quiz_sup": f"{all_sup}/{all_quiz}",
        "summary_ok": f"{all_sum_ok}/{len(raw_runs)}",
        "shorter": f"{all_shorter}/{len(raw_runs)}",
        "village_fmt": f"{all_vil}/{len(raw_runs)}",
        "village_rel": f"{all_vil}/{len(raw_runs)}",
        "words_exp": f"{all_exp}/{all_cands}",
        "offline_status": "OFFLINE" if (raw_runs and all(r.get("offline_status") == "OFFLINE" for r in raw_runs)) else "ONLINE"
    }

    full_bench = {
        "meta": {
            "model": m_name,
            "pte_path": pte_p,
            "backend": "mock" if is_mock else "executorch",
            "runs_per_passage": runs_per_p,
            "offline_status": overall["offline_status"]
        },
        "summary": summary_rows,
        "overall": overall
    }
    return full_bench

def run_worker(args):
    cfg = load_cfg(args.config)
    m_cfg = cfg.get("model", {})
    r_cfg = cfg.get("runtime", {})

    if args.require_offline:
        net = get_net_state()
        if not net.get("is_offline"):
            sys.exit("Error: system is ONLINE; --require-offline specified.")

    base_rss = round(psutil.Process().memory_info().rss / (1024 * 1024), 2)

    pte_p = args.pte or m_cfg.get("pte", "")
    tok_p = args.tokenizer or m_cfg.get("tokenizer", "")
    m_name = m_cfg.get("name", "Llama-3.2-1B-Instruct")
    is_mock = args.mock or r_cfg.get("mock", False)
    gl_p = args.glossary or "data/tamil_glossary.json"
    gl = load_gl(gl_p) if os.path.exists(gl_p) else {}

    p1_max = int(m_cfg.get("max_new_pass1", 320))
    p2_max = int(m_cfg.get("max_new_pass2", 280))

    p_path = f"samples/{args.passage}.txt"
    with open(p_path, "r", encoding="utf-8") as f:
        p_txt = f.read()
    w_cnt = len(p_txt.split())

    t_load_0 = time.perf_counter()
    if is_mock or not pte_p:
        bk = MockBackend()
    else:
        bk = ETBackend(pte_p, tok_p)
    load_time = round(time.perf_counter() - t_load_0, 3)

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

    ru_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_rss = round(ru_rss / (1024 * 1024) if platform.system() == "Darwin" else ru_rss / 1024, 2)

    telem_res = collect_telem(
        m_name=m_name,
        pte_path=pte_p,
        tok_cnt=pipe_res["tok_cnt"],
        inf_time=inf_sec,
        is_mock=getattr(bk, "is_mock", False)
    )
    telem_res["peak_rss_mib"] = peak_rss
    telem_res["peak_rss_mb"] = peak_rss

    rep_txt = build_report(pipe_res, telem_res)
    if args.out_txt:
        with open(args.out_txt, "w", encoding="utf-8") as f:
            f.write(rep_txt)

    tot_retries = pipe_res["p1_info"]["retries"] + pipe_res["p2_info"]["retries"]
    r_reasons = []
    if pipe_res["p1_info"]["retried"]:
        r_reasons.append(pipe_res["p1_info"]["reason"])
    if pipe_res["p2_info"]["retried"]:
        r_reasons.append(pipe_res["p2_info"]["reason"])

    record = {
        "passage": args.passage,
        "run": args.run_idx,
        "words": w_cnt,
        "load_time_sec": load_time,
        "baseline_rss_mib": base_rss,
        "peak_rss_mib": peak_rss,
        "p1_sec": pipe_res["p1_info"]["seconds"],
        "p1_tokens": pipe_res["p1_info"]["tokens"],
        "p1_retries": pipe_res["p1_info"]["retries"],
        "p1_retried": pipe_res["p1_info"]["retried"],
        "p1_retry_reason": pipe_res["p1_info"]["reason"],
        "p1_attempts": pipe_res["p1_info"]["attempts"],
        "p2_sec": pipe_res["p2_info"]["seconds"],
        "p2_tokens": pipe_res["p2_info"]["tokens"],
        "p2_retries": pipe_res["p2_info"]["retries"],
        "p2_retried": pipe_res["p2_info"]["retried"],
        "p2_retry_reason": pipe_res["p2_info"]["reason"],
        "p2_attempts": pipe_res["p2_info"]["attempts"],
        "inf_time_sec": inf_sec,
        "tokens": pipe_res["tok_cnt"],
        "tok_per_sec": telem_res["tok_per_sec"],
        "retries": tot_retries,
        "retry_reasons": "; ".join(r_reasons) if r_reasons else "none",
        "quiz_count": len(pipe_res["parsed"]["quiz"]),
        "quiz_incomplete": pipe_res["guards"]["quiz_incomplete"],
        "summary_fallback": pipe_res["p1_info"].get("summary_fallback", False),
        "summary_ok": pipe_res["guards"]["summary_produced_without_fallback"],
        "guards": pipe_res["guards"],
        "offline_status": "OFFLINE" if telem_res["net"]["is_offline"] else "ONLINE",
        "telemetry": telem_res,
        "pipeline": pipe_res
    }

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

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

    os.makedirs(args.out_dir, exist_ok=True)
    raw_runs = []

    for p_name in PASSAGES:
        p_path = f"samples/{p_name}.txt"
        if not os.path.exists(p_path):
            continue

        for r_idx in range(1, args.runs + 1):
            print(f"Running {p_name} in fresh subprocess (run {r_idx}/{args.runs})...", flush=True)
            run_txt_p = os.path.join(args.out_dir, f"{p_name}_{r_idx}.txt")
            run_json_p = os.path.join(args.out_dir, f"{p_name}_{r_idx}.json")

            cmd = [
                sys.executable, "scripts/bench.py",
                "--worker",
                "--passage", p_name,
                "--run-idx", str(r_idx),
                "--config", args.config,
                "--out-json", run_json_p,
                "--out-txt", run_txt_p
            ]
            if args.pte:
                cmd += ["--pte", args.pte]
            if args.tokenizer:
                cmd += ["--tokenizer", args.tokenizer]
            if is_mock:
                cmd.append("--mock")
            if args.require_offline:
                cmd.append("--require-offline")

            sub_res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="replace")
            if sub_res.returncode != 0:
                print(f"Worker failed for {p_name}_{r_idx}:\n{sub_res.stderr}", file=sys.stderr)
                sys.exit(sub_res.returncode)

            with open(run_json_p, "r", encoding="utf-8") as f:
                record = json.load(f)
            raw_runs.append(record)

    full_bench = compute_benchmark_stats(
        raw_runs,
        m_name=m_name,
        pte_p=pte_p,
        is_mock=is_mock,
        runs_per_p=args.runs
    )

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
        "| Passage | Words | Latency (s) | Tokens | Tokens/s | Peak RSS (MiB) [Base] | Retries (Reasons) | Quizzes | Model Cite | Quiz Sup | Summary OK | Shorter | Village | Words Exp | Offline |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in full_bench["summary"]:
        md_lines.append(
            f"| {row['passage']} | {row['words']} | {row['inf_time']} | {row['tokens']} | {row['tps']} | {row['rss']} [{row['base_rss']}] | {row['retries']} ({row['reasons']}) | {row['quiz_items']} | {row.get('quiz_model_cite', '-')} | {row['quiz_sup']} | {row['summary_ok']} | {row['shorter']} | {row['village_fmt']} | {row['words_exp']} | {row['offline_status']} |"
        )
    ov = full_bench["overall"]
    md_lines.append(
        f"| **{ov['passage']}** | **{ov['words']}** | **{ov['inf_time']}** | **{ov['tokens']}** | **{ov['tps']}** | **{ov['rss']} [{ov['base_rss']}]** | **{ov['retries']}** | **{ov['quiz_items']}** | {ov.get('quiz_model_cite', '-')} | {ov['quiz_sup']} | **{ov['summary_ok']}** | **{ov['shorter']}** | **{ov['village_fmt']}** | **{ov['words_exp']}** | **{ov['offline_status']}** |"
    )
    md_lines.append("")

    with open(args.summary_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"\n[Benchmark complete]: Saved {args.summary_json} and {args.summary_md}")

def main():
    p = argparse.ArgumentParser(description="StudyAid Benchmark Runner")
    p.add_argument("--worker", action="store_true", default=False)
    p.add_argument("--passage", default="optics")
    p.add_argument("--run-idx", type=int, default=1)
    p.add_argument("--config", default="config.toml")
    p.add_argument("--pte", default=None)
    p.add_argument("--tokenizer", default=None)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--glossary", default="data/tamil_glossary.json")
    p.add_argument("--out-dir", default="evidence/runs")
    p.add_argument("--out-json", default=None)
    p.add_argument("--out-txt", default=None)
    p.add_argument("--summary-json", default="evidence/benchmark.json")
    p.add_argument("--summary-md", default="evidence/benchmark.md")
    p.add_argument("--require-offline", action="store_true", default=False)
    p.add_argument("--mock", action="store_true", default=False)

    args = p.parse_args()
    if args.worker:
        run_worker(args)
    else:
        run_bench(args)

if __name__ == "__main__":
    main()
