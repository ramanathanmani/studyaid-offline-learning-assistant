#!/bin/bash
set -e
cd /home/rock/.gemini/antigravity/scratch/studyaid/eval_kit
VENV="/home/rock/.gemini/antigravity/scratch/studyaid/.venv/bin/python"

echo "Starting Hold-out Evaluation Shards (2 shards, 15 paragraphs each = 30 hold-out paragraphs)..."

STUDYAID_THREADS=4 $VENV run_eval.py corpus.jsonl hold.0.jsonl --split hold --shard 0/2 --limit 15 > hold.0.log 2>&1 &
P0=$!
echo "Hold Shard 0 launched (PID $P0)"

STUDYAID_THREADS=4 $VENV run_eval.py corpus.jsonl hold.1.jsonl --split hold --shard 1/2 --limit 15 > hold.1.log 2>&1 &
P1=$!
echo "Hold Shard 1 launched (PID $P1)"

wait $P0
echo "Hold Shard 0 finished."
wait $P1
echo "Hold Shard 1 finished."

echo "Combining hold shards into hold.jsonl..."
cat hold.0.jsonl hold.1.jsonl > hold.jsonl

echo "Generating final_report_laptop.md and gold.csv..."
$VENV report.py corpus.jsonl hold.jsonl glossary.json --bank example_bank.json --gold 30 --out final_report_laptop.md

echo "Generating honest_report.md..."
$VENV report.py corpus.jsonl hold.jsonl glossary_honest.json --bank example_bank.json --out honest_report.md

echo "Hold-out evaluation complete!"
