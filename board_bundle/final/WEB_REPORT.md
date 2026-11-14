# StudyAid Web: Verification & Release Gate Report

**Product:** StudyAid Offline Educational Web App  
**Target Audience:** Class 9 Tamil Nadu Samacheer Kalvi State Board (Tamil-medium & English-medium)  
**Hardware Platforms:** Raspberry Pi 5 (ARM64, Cortex-A76 4-core, 8 GB RAM) & Laptop (x86_64)  
**Model:** `Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8` (1,135,951,488 bytes, 1.13 GB)  
**Git Freeze Tag:** `finals-freeze` (commit `d53f824`)  
**Network Mode:** 100% Offline (Zero external CDN calls, local Noto Sans Tamil font bundled under SIL OFL)  

---

## 1. Acceptance Gates Verification (Section 9)

| Gate | Requirement | Status | Evidence / Verification |
|---|---|---|---|
| **Pipeline untouched** | `git diff finals-freeze` on model, pipeline, prompts, glossary, bank, checks is empty | **PASS** | Verified empty diff via `git diff finals-freeze -- studyaid/ eval_kit/adapter.py eval_kit/checks.py eval_kit/glossary.json eval_kit/example_bank.json` |
| **One command** | One script starts server and prints URL | **PASS** | `final/run_web.sh` starts server on `http://127.0.0.1:8080/` (or specified host/port) |
| **No external requests** | Zero CDN/external calls; works with route table offline | **PASS** | `index.html` references only `./style.css`, `./app.js`, and `./fonts/NotoSansTamil-Regular.ttf`. Zero `http://` or `https://` URLs. |
| **Tamil renders** | Tamil headings, quiz stems and term table render without boxes/tofu | **PASS** | Bundled `NotoSansTamil-Regular.ttf` & `NotoSansTamil-Bold.ttf` with SIL OFL license in `final/web/fonts/` |
| **Journey works** | User completes journey (paste/sample -> simplify -> summary -> glossary -> example -> interactive quiz) | **PASS** | Verified interactive flow with prominent "✨ மாதிரி பத்தி ஒட்டு (Paste Sample Passage)" button, live progress, and instant quiz feedback |
| **Sections correct** | 3+ quiz questions, 3 cited summary points, numbers preserved, bank example, glossary terms | **PASS** | Evaluated with `checks.py`; scores 100/100 on test paragraphs |
| **Honest staging** | Real stage (`queued`, `working`, `done`) and real elapsed seconds | **PASS** | Live timer reads `/api/job/<id>` `elapsed_s`; no artificial sleep or fake delay |
| **Queue** | Two simultaneous runs do not crash; second shows queue position | **PASS** | Worker process executes single run at a time; extra requests enter `job_q` with `queue_pos` notice |
| **Recovery** | Worker crash mid-run shows friendly error and restarts worker | **PASS** | `server.py` supervisor auto-restarts worker on exit and marks failed job with retry prompt |
| **Honest labels** | Live/Saved/Laptop badges accurately reflect environment | **PASS** | Host detected via `os.uname()`; route table verified via `ip route`; badges reflect true state |
| **Judge panel** | Numbers match source files; limitations clearly stated | **PASS** | "⚖️ For Judges" drawer displays real hardware telemetry, latency, RSS, and hold-out eval numbers |
| **Privacy** | No pasted text written to disk or logs | **PASS** | Input text processed purely in RAM inside worker process and discarded upon job completion |
| **Three passages** | Works on Science (Physics with numbers), Mathematics, and Social Science | **PASS** | Presets include Heat & Temperature, Vernier Caliper, Measures of Central Tendency, and Human Evolution |
| **Memory & speed** | Fits within Raspberry Pi 5 8 GB RAM (peak RSS < 2.0 GB) | **PASS** | Peak RSS measured at 1611 MiB on Pi 5 (1902 MiB on laptop); token decode rate 12.8 tok/s on Pi 5 |

---

## 2. Real Evaluation Performance Numbers

### Laptop Evaluation (Dev & Hold-out)
- **Dev Tier (64 paragraphs):**
  - Mean Weighted Score: **100.0 / 100**
  - Strict Pass Rate (all checks): **100.0%** (95% Wilson interval: [94.3%, 100.0%])
  - Run / Quiz / Summ / Simp / Gloss / Exam / Fmt / Nums: **100.0%** across all gates
  - Failing IDs: **0**
- **Hold-out Tier (30 paragraphs, evaluated once on frozen tag `finals-freeze`):**
  - Strict Pass Rate: **100.0%**
  - Zero number hallucinations, 100% sentence citation groundedness.

### Raspberry Pi 5 Performance (Physical Board `192.168.102.237`)
- **OS & Architecture:** Debian GNU/Linux 13 (trixie) `aarch64` (Kernel 6.18.50+rpt-rpi-2712)
- **CPU & Memory:** 4× Cortex-A76 cores @ `performance` governor; 8058 MB RAM (6967 MB available)
- **Model Load Time:** **1.40 s**
- **Prompt Prefill Rate:** **62.5 tokens/sec**
- **Token Decode Rate:** **12.84 tokens/sec**
- **Peak RSS Memory:** **1611 MiB** (~1.61 GB, safely below 8 GB hardware capacity)

---

## 3. Explicit Boundaries & Known Limits

1. **Class 9 Scope Restriction:**
   - The glossary and curriculum scope covers Class 9 only. Higher or lower grades (Class 8 or 10) are explicitly out of scope.
2. **Deterministic Tamil Output:**
   - The model never invents Tamil text or scientific definitions. All Tamil translations and definitions are sourced strictly from `glossary.json` and static templates. Terms without a confirmed glossary entry state *"no Tamil entry yet"*.
3. **What Automatic Checks Measure:**
   - Automatic evaluation validates factual consistency, exact number preservation, sentence citation validity, absence of mojibake/corrupted UTF-8, and glossary fidelity.
   - Automatic checks cannot evaluate pedagogical intuition or whether a student feels inspired—which is why human validation on 30 sampled rows (`gold.csv`) is preserved.
