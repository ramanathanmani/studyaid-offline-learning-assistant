#!/bin/bash
set -e
cd /home/rock/.gemini/antigravity/scratch/studyaid/eval_kit
VENV="/home/rock/.gemini/antigravity/scratch/studyaid/.venv/bin/python"

echo "Starting Dev Evaluation Shards (2 shards, 50 paragraphs each = 100 paragraphs total)..."

STUDYAID_THREADS=4 $VENV run_eval.py corpus.jsonl dev.0.jsonl --split dev --shard 0/2 --limit 50 > dev.0.log 2>&1 &
P0=$!
echo "Shard 0 launched (PID $P0)"

STUDYAID_THREADS=4 $VENV run_eval.py corpus.jsonl dev.1.jsonl --split dev --shard 1/2 --limit 50 > dev.1.log 2>&1 &
P1=$!
echo "Shard 1 launched (PID $P1)"

echo "Waiting for shards to complete..."
wait $P0
echo "Shard 0 finished."
wait $P1
echo "Shard 1 finished."

echo "Running report.py across all dev shards..."
$VENV report.py corpus.jsonl "dev.*.jsonl" glossary.json --bank example_bank.json --out eval_report.md
echo "Dev evaluation and report complete!"
