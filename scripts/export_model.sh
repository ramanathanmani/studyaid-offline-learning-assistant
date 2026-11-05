#!/usr/bin/env bash
set -euo pipefail

cat << 'EOF'
================================================================================
ExecuTorch Export Guide: Llama 3.2 1B Instruct (4-bit XNNPACK)
================================================================================

PREREQUISITES:
1. Gated Access: Obtain approved access for Meta Llama 3.2 on HuggingFace or Meta AI.
2. ExecuTorch Environment:
   git clone https://github.com/pytorch/executorch.git
   cd executorch
   git submodule update --init --recursive
   ./install_requirements.sh

EXPORT INSTRUCTIONS (4-bit weight, 8-bit dynamic activation XNNPACK):

Step 1: Download Llama 3.2 1B Instruct weights locally into a folder:
   e.g., ./checkpoints/Llama-3.2-1B-Instruct/
   Files required:
     - consolidated.00.pth (or model.safetensors converted)
     - params.json
     - tokenizer.model (or tokenizer.json)

Step 2: Run ExecuTorch export utility:
   python -m executorch.extension.llm.export.export_llm \
     --config examples/models/llama/config/llama_q8da4w.yaml \
     +base.model_class="llama3_2" \
     +base.checkpoint="./checkpoints/Llama-3.2-1B-Instruct/consolidated.00.pth" \
     +base.params="./checkpoints/Llama-3.2-1B-Instruct/params.json" \
     +'+base.metadata="{\"get_bos_id\":128000, \"get_eos_ids\":[128009, 128001], \"get_max_context_len\":4096}"' \
     --output_name llama3_2_1b_q4_xnnpack.pte

Step 3: Point studyaid to the exported files:
   python -m studyaid run \
     --passage samples/optics.txt \
     --pte ./llama3_2_1b_q4_xnnpack.pte \
     --tokenizer ./checkpoints/Llama-3.2-1B-Instruct/tokenizer.model

NOTE: Model weights are gated. This script does not download weights.
================================================================================
EOF
