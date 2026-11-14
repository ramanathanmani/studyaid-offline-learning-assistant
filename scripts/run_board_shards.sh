#!/bin/bash
set -e
cd /home/rock/studyaid
VENV="/home/rock/studyaid/.venv/bin/python"

echo "Starting 30-Paragraph Board Run (2 shards, 15 paragraphs each)..."

STUDYAID_THREADS=2 $VENV eval_kit/run_eval.py board_bundle/board_corpus.jsonl board_eval.0.jsonl --split hold --shard 0/2 --limit 15 > board_eval.0.log 2>&1 &
P0=$!
echo "Board Shard 0 launched (PID $P0)"

STUDYAID_THREADS=2 $VENV eval_kit/run_eval.py board_bundle/board_corpus.jsonl board_eval.1.jsonl --split hold --shard 1/2 --limit 15 > board_eval.1.log 2>&1 &
P1=$!
echo "Board Shard 1 launched (PID $P1)"

wait $P0
echo "Board Shard 0 finished."
wait $P1
echo "Board Shard 1 finished."

echo "Combining board shards into board_eval.jsonl..."
cat board_eval.0.jsonl board_eval.1.jsonl > board_eval.jsonl

echo "Generating final_report_board.md..."
$VENV eval_kit/report.py board_bundle/board_corpus.jsonl board_eval.jsonl eval_kit/glossary.json --bank eval_kit/example_bank.json --out final_report_board.md

echo "Board evaluation complete!"
