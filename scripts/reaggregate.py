import glob
import json
import os
import sys

sys.path.insert(0, ".")
from scripts.bench import compute_benchmark_stats

raw_runs = []
for p in sorted(glob.glob("evidence/runs/*.json")):
    with open(p, "r", encoding="utf-8") as f:
        raw_runs.append(json.load(f))

res = compute_benchmark_stats(
    raw_runs,
    m_name="Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8",
    pte_p="models/llama1b/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte",
    is_mock=False,
    runs_per_p=3
)

with open("evidence/benchmark.json", "w", encoding="utf-8") as f:
    json.dump(res, f, indent=2, ensure_ascii=False)

md_lines = [
    "# StudyAid Benchmark Results",
    "",
    f"**Model:** {res['meta']['model']}  ",
    f"**Backend:** Real ExecuTorch  ",
    f"**Runs per passage:** 3  ",
    f"**Status:** {res['meta']['offline_status']}  ",
    "",
    "| Passage | Words | Latency (s) | Tokens | Tokens/s | Peak RSS (MiB) [Base] | Retries (Reasons) | Quizzes | Model Cite | Quiz Sup | Summary OK | Shorter | Village | Words Exp | Offline |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
]
for row in res["summary"]:
    mc = row.get("quiz_model_cite", "-")
    md_lines.append(
        f"| {row['passage']} | {row['words']} | {row['inf_time']} | {row['tokens']} | {row['tps']} | {row['rss']} [{row['base_rss']}] | {row['retries']} ({row['reasons']}) | {row['quiz_items']} | {mc} | {row['quiz_sup']} | {row['summary_ok']} | {row['shorter']} | {row['village_fmt']} | {row['words_exp']} | {row['offline_status']} |"
    )
ov = res["overall"]
ov_mc = ov.get("quiz_model_cite", "-")
md_lines.append(
    f"| **{ov['passage']}** | **{ov['words']}** | **{ov['inf_time']}** | **{ov['tokens']}** | **{ov['tps']}** | **{ov['rss']} [{ov['base_rss']}]** | **{ov['retries']}** | **{ov['quiz_items']}** | **{ov_mc}** | **{ov['quiz_sup']}** | **{ov['summary_ok']}** | **{ov['shorter']}** | **{ov['village_fmt']}** | **{ov['words_exp']}** | **{ov['offline_status']}** |"
)
md_lines.append("")

with open("evidence/benchmark.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines) + "\n")

print("Re-aggregated benchmark.json and benchmark.md successfully.")
