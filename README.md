# StudyAid: Offline Smart Learning Assistant

Offline Smart Learning Assistant: ExecuTorch + Llama 3.2 1B study aid for rural Tamil Nadu students (Namma AI Hackathon PoC).

- **Install:** `pip install -e .`
- **Run:** `python -m studyaid run --passage samples/optics.txt`
- **Notice & Attribution:** See [NOTICE.md](NOTICE.md) for Llama 3.2 Community License and "Built with Llama" details.

> **Built with Llama**
> This project uses Meta Llama 3.2 1B Instruct, licensed under the [Llama 3.2 Community License Agreement](https://www.llama.com/llama3_2/license/).
> Pre-exported 4-bit ExecuTorch model source: [`executorch-community/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8-ET`](https://huggingface.co/executorch-community/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8-ET). Model weights are not included in this repository.


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

> **Hardware Label: Development Laptop (x86_64), NOT Raspberry Pi**  
> All measurements below were collected using real ExecuTorch runtime inference with `Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte`. Raspberry Pi 5 ARM benchmark metrics will be recorded separately during finals hardware handover.

### Host Platform
| Property | Value |
|---|---|
| Device / Form Factor | Development Laptop (`HOST: laptop (not Raspberry Pi)`) |
| Processor | 11th Gen Intel(R) Core(TM) i7-1185G7 @ 3.00GHz |
| CPU Cores | 8 |
| Total RAM | 14.3 GB |
| Operating System | Linux 7.0.0-38-generic (Ubuntu x86_64) |
| Virtual Env | Python 3.14.4 (`.venv`) |
| ExecuTorch Version | 1.6.0 |
| PyTorch Version | 2.15.0 |

### Standalone Smoke Test (`scripts/smoke_test.py`)
- **Prompt:** "Explain in one sentence why a pencil looks bent in a glass of water."
- **Generated Answer:** *"A pencil looks bent in a glass of water because light slows down and changes direction when it moves from air into water, causing the light rays to bend."*
- **Model Load Time:** 2.238 s
- **Tokens Generated:** 41 tokens
- **Inference Time:** 4.644 s
- **Decode Rate:** 17.70 tokens/sec (Prefill: 108.80 tokens/sec; Overall: 8.83 tokens/sec)
- **Model `.pte` Size:** 1,083.33 MB (1,135,951,488 bytes)
- **Peak RSS:** 1,727.76 MB

### Full Pipeline End-to-End (`samples/optics.txt`)
- **Passage:** 5 sentences on Refraction of Light (84 words)
- **Execution Mode:** `[REAL EXECUTORCH RUN]` (Two-Pass generation)
- **Model Load Time:** ~2.00 s
- **Total Inference Time:** 19.432 s
- **Total Tokens Generated:** 273 tokens
- **Overall Inference Rate:** 14.05 tokens/sec
  - *Pass 1 (Content Simplification & Glossary):* 173 tokens generated in 9.61 s (17.99 tokens/sec decode, 208.30 tokens/sec prefill)
  - *Pass 2 (Grounded Quiz Generation):* 98 tokens generated in 5.17 s (18.95 tokens/sec decode, 210.74 tokens/sec prefill)
- **Peak Process RSS:** 1,909.30 MB
- **Run Artifacts:** Saved in `outputs/run_20261105_150929.txt` and `outputs/run_20261105_150929.json`
