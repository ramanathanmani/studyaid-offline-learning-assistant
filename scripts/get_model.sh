#!/usr/bin/env bash
set -euo pipefail

m_id="executorch-community/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8-ET"
tgt_dir="models/llama1b"

mkdir -p "$tgt_dir"

python3 -c "
import sys
from huggingface_hub import snapshot_download

repo = '$m_id'
dest = '$tgt_dir'
snapshot_download(repo_id=repo, local_dir=dest)
"
