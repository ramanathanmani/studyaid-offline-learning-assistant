# StudyAid: Offline Smart Learning Assistant

Offline Study Aid using ExecuTorch and Llama 3.2 1B Instruct, tailored for Class 8-10 students in rural Tamil Nadu government schools.

## 1. What It Is
StudyAid is a fully offline, zero-network Python CLI tool built for inclusive education. It processes a 150-300 word English textbook passage and generates:
1. Sentence-level indexing (`[S1]`..`[Sn]`) and hardest sentence detection.
2. Readability metrics before and after plain-English sentence simplification.
3. A concise 2-3 sentence summary.
4. An everyday village-life analogy connecting scientific concepts to rural experiences.
5. Simple English meanings for hard words with seed Tamil terms from a verified-flagged local glossary.
6. Three passage-grounded quiz questions with automated citation support checking.
7. A "JUDGE PROOF" telemetry block with verified offline hardware and execution metrics.

## 2. Setup
Requires Python 3.10+ (Standard library first).

```bash
git clone <repo-url> studyaid
cd studyaid

# Install dependencies (psutil, pytest)
pip install psutil pytest

# ExecuTorch is required only for real model inference
pip install executorch
```

## 3. How to Export the Model
Llama 3.2 weights are gated by Meta. Do not download weights automatically.

To view the exact current export steps:
```bash
./scripts/export_model.sh
```

Summary:
1. Obtain approved gated access to `meta-llama/Llama-3.2-1B-Instruct`.
2. Convert and export using ExecuTorch 4-bit XNNPACK (`llama_q8da4w.yaml`):
   ```bash
   python -m executorch.extension.llm.export.export_llm \
     --config examples/models/llama/config/llama_q8da4w.yaml \
     +base.model_class="llama3_2" \
     +base.checkpoint="/path/to/consolidated.00.pth" \
     +base.params="/path/to/params.json" \
     +'+base.metadata="{\"get_bos_id\":128000, \"get_eos_ids\":[128009, 128001], \"get_max_context_len\":4096}"' \
     --output_name llama3_2_1b_q4_xnnpack.pte
   ```

## 4. How to Run

### Check Offline Status
Inspect network interfaces and default routing table without inference:
```bash
python -m studyaid check-offline
```

### Run with Mock Backend (offline proof of concept)
```bash
python -m studyaid run --passage samples/optics.txt --mock
# or
./scripts/demo.sh
```

### Run with Real ExecuTorch Runtime
```bash
python -m studyaid run \
  --passage samples/optics.txt \
  --pte /path/to/llama3_2_1b_q4_xnnpack.pte \
  --tokenizer /path/to/tokenizer.model
```

### Options
- `--passage PATH`: Path to passage text file (warns if outside 150-300 words).
- `--pte PATH`: Path to `.pte` exported ExecuTorch model.
- `--tokenizer PATH`: Path to tokenizer file (`.model` or `.bin`).
- `--two-pass`: Enable two-pass generation (pass 1: simple/summary/village/words, pass 2: quiz).
- `--mock`: Force mock backend mode.
- `--config PATH`: Path to config file (default: `config.toml`).
- `--out-dir PATH`: Output directory for timestamped `.txt` and `.json` runs (default: `outputs`).

## 5. How to Run the Tests
Tests require no model weights and no network access:
```bash
pytest tests/
```

## 6. Project Structure
```
studyaid/
  README.md
  pyproject.toml
  config.toml
  data/
    tamil_glossary.json
  samples/
    optics.txt
    expected_optics.txt
    photosynthesis.txt
  scripts/
    export_model.sh
    demo.sh
  studyaid/
    __init__.py
    __main__.py
    cli.py
    sents.py
    hard.py
    gloss.py
    backend.py
    prompt.py
    parse.py
    check.py
    readab.py
    telem.py
    pipeline.py
    render.py
  tests/
    test_sents.py
    test_hard.py
    test_gloss.py
    test_parse.py
    test_check.py
    test_readab.py
    test_telem.py
    test_pipeline.py
  outputs/
    .gitkeep
```

## 7. Honest Limitations
- **Small-Model Errors:** Llama 3.2 1B Instruct is lightweight for edge devices; it can occasionally omit tags or hallucinate citations. The pipeline includes automatic retry and tag recovery, but small models remain susceptible to generation variance.
- **Keyword-Overlap Verification:** Quiz citation support is determined by lexical token overlap between answer tokens and the cited sentence. This is an efficient edge heuristic, not formal semantic or logical proof.
- **Unverified Seed Glossary:** All seed Tamil entries in `data/tamil_glossary.json` are marked `"verified": false`. They must be independently validated against Samacheer Kalvi state curriculum textbooks by a Tamil-speaking educator before classroom deployment.
- **Laptop vs Raspberry Pi Telemetry:** All current measurements are taken on the development laptop host. Hardware telemetry explicitly labels the host machine. Raspberry Pi 5 measurements will be conducted at the hackathon finals upon hardware handover.

## 8. Measured Results
*(This section stays empty until real model runs with `.pte` weights are executed on the host or Raspberry Pi hardware.)*
