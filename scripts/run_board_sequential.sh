#!/bin/bash
set -e
cd /home/rock/studyaid
VENV="/home/rock/studyaid/.venv/bin/python"

echo "Starting 30-Paragraph Board Run (Single Process, 4 threads)..."
export OMP_NUM_THREADS=4
export STUDYAID_THREADS=4

$VENV eval_kit/run_eval.py board_bundle/board_corpus.jsonl board_eval.jsonl --split hold --limit 30 > board_eval.log 2>&1

echo "Generating final_report_board.md..."
$VENV eval_kit/report.py board_bundle/board_corpus.jsonl board_eval.jsonl eval_kit/glossary.json --bank eval_kit/example_bank.json --out final_report_board.md

echo "Board evaluation complete!"
