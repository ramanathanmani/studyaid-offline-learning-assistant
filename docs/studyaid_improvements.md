# StudyAid: Improvements for Model and Project

Review of the temperature-passage run (Llama-3.2-1B-Instruct-SpinQuant INT4, ExecuTorch, laptop), prepared for the Namma AI hackathon.

---

## 1. What the current output shows

| Section | Status | Problem |
|---|---|---|
| Simplified sentence | Weak | Drops the triple-point explanation, so it is shorter but not easier |
| Readability metrics | Weak | Only words and letters; neither measures difficulty |
| Summary | Weak | One generic line, no key points, no citations |
| Village example | Wrong | Kumbakonam hot springs is not a fact to rely on, and it is unrelated to measuring temperature |
| Glossary | Fails | Every entry says "English only"; two definitions are factually wrong |
| Quiz | Fails | 2 of 3 questions; the problem statement needs at least 3 |
| Telemetry | Needs rerun | Shows ONLINE with wifi up and a default route, which weakens the offline claim |

---

## 2. Model output improvements

### 2.1 Fix the village example
- Do not let the 1B model invent places or facts.
- Keep a small bank of local examples tagged by topic. Pick one by keyword match, and let the model only phrase it.
- Examples for this passage:
  - A Chennai afternoon in May is about 40 °C, while Ooty can be about 15 °C. A thermometer gives each as a number.
  - A clinical thermometer: normal body temperature is about 37 °C.
  - A kettle: water boils at 100 °C, so the kettle is hotter than the tap water.

### 2.2 Fix the glossary (accuracy first)
Wrong entries in the current run:

| Term | Current output | Correct idea |
|---|---|---|
| fahrenheit | "scale with 100 as base" | Scale where water freezes at 32 °F and boils at 212 °F |
| saturated | "completely dissolved" | Holding the maximum amount of vapour possible at that temperature |
| equilibrium | "balance of temperature and pressure" | State where nothing changes any more because everything is balanced |

Rule: the model never writes a definition. The glossary file holds every English and Tamil definition. The model (or a plain keyword match) only decides which entries appear.

### 2.3 Fix the simplified sentence
Current: "One kelvin is the fraction (1/273.16) of the thermodynamic temperature of the triple point of water."
This removed the only part that explained the triple point.

Better, as two short sentences:
- The triple point of water is the temperature at which pure water exists as ice, liquid and vapour together.
- One kelvin is 1/273.16 of that temperature.

Add a check that every number in the original (here 273.16) appears unchanged in the simplified text.

### 2.4 Better readability metrics
Keep the before/after table, and add:
- Number of sentences
- Average words per sentence
- Syllables per word (or a Flesch-style score)
- Count of glossary terms in the sentence

Do not present "fewer words" as "easier". Show it alongside sentence length and difficult-term count.

### 2.5 Make the quiz always reach 3 questions
1. Generate with the model.
2. Validate each question: answer appears in the cited sentence, the question is not a duplicate, and the answer is short.
3. If fewer than 3 pass, retry up to 2 times with a lower temperature.
4. If still short, build fill-in-the-blank questions directly from the passage sentences (for example blank out "kelvin" in S2).
5. Add 3 distractors for multiple-choice, taken from other terms in the glossary.

Specific fixes:
- Q1 asks for "the other unit" but the answer lists two. Ask "Name one other unit besides kelvin" or "Name two other units".
- The support check prints stemmed fragments like `celsiu` and `degre`. Show whole words, and require at least 60% overlap with the cited sentence.

### 2.6 Better summary
Replace the one-line summary with 3 points, each citing a sentence:
- Temperature measures how hot or cold something is [S1]
- The SI unit is the kelvin, and 0 K is absolute zero [S2, S4]
- Other units are degree Celsius and Fahrenheit [S5]

### 2.7 Better hard-word picking
"temperature" and "fahrenheit" were picked, but "triple point" and "absolute zero" are the real barriers. Rank candidates by:
1. Present in the glossary
2. Not in a common-words list
3. Appears in the hardest sentence

Show the top 5 only.

---

## 3. Tamil glossary integration

### 3.1 Design
- Do not ask Llama 3.2 1B to write Tamil. Small models are weak at it and will produce confident mistakes.
- Use a curated bilingual JSON glossary as the single source of truth.
- Use fixed Tamil templates for headings, quiz stems and feedback ("கேள்வி", "விடை", "சரி / தவறு").
- Show each hard term as: English term, Tamil term, simple English meaning, simple Tamil meaning.
- If a term has no glossary entry, print "no Tamil entry yet". Never let the model guess.

### 3.2 Glossary schema (`glossary.json`)

```json
{
  "temperature": {
    "ta": "வெப்பநிலை",
    "en_def": "How hot or cold something is.",
    "ta_def": "ஒரு பொருள் எவ்வளவு சூடாக அல்லது குளிராக உள்ளது என்பதன் அளவு.",
    "sub": "physics",
    "ok": true
  },
  "absolute zero": {
    "ta": "தனிச் சுழி வெப்பநிலை",
    "en_def": "The lowest possible temperature, 0 K.",
    "ta_def": "மிகக் குறைந்த சாத்தியமான வெப்பநிலை, 0 K.",
    "sub": "physics",
    "ok": false
  }
}
```

### 3.3 Starter entries for this passage

| English | Tamil | Simple meaning (English) |
|---|---|---|
| temperature | வெப்பநிலை | How hot or cold something is |
| kelvin | கெல்வின் | The SI unit of temperature |
| absolute zero | தனிச் சுழி வெப்பநிலை | The lowest possible temperature, 0 K |
| triple point | மும்மைப் புள்ளி | The one temperature where ice, water and vapour stay together |
| thermodynamic | வெப்ப இயக்கவியல் | About how heat and energy move and change |
| equilibrium | சமநிலை | A state where nothing changes because everything is balanced |
| saturated vapour | நிறைவுற்ற நீராவி | Vapour holding the most it can at that temperature |
| degree Celsius | டிகிரி செல்சியஸ் | Scale where water freezes at 0 and boils at 100 |
| Fahrenheit | பாரன்ஹீட் | Scale where water freezes at 32 and boils at 212 |
| melting ice | உருகும் பனிக்கட்டி | Ice that is turning into water |

Check the Tamil terms above against the Tamil Nadu State Board Class 8-10 science textbook wording before submission. Textbook wording is what the students will recognise.

### 3.4 Lookup code

```python
import json, re

def load_gl(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def find_terms(txt, gl):
    low = txt.lower()
    hits = []
    for t in sorted(gl, key=len, reverse=True):
        if re.search(r"\b" + re.escape(t) + r"s?\b", low):
            hits.append(t)
            low = low.replace(t, " ")
    return hits

def render(txt, gl, top=5):
    rows = []
    for t in find_terms(txt, gl)[:top]:
        e = gl[t]
        rows.append(f"- {t} / {e['ta']}: {e['en_def']} | {e['ta_def']}")
    return "\n".join(rows)
```

### 3.5 Build the glossary from the Samacheer Kalvi textbooks

The organisers' passage is unknown, so the glossary must cover the whole Class 8-10 syllabus. Build it from the textbooks themselves instead of typing terms by hand.

**Scope:** technical terms (கலைச்சொற்கள்), not every word in the books. Cover Science and Maths first, then Social Science.

**Source:** the official Tamil Nadu Textbook Corporation site, `tntextbooks.in`. Class 8 science is split into three terms, and both Tamil-medium and English-medium PDFs are available for classes 8, 9 and 10.
Check the site's terms of use and keep a source note (book, class, page) on every entry.

**Steps**
1. Download Class 8, 9 and 10 books for Science, Maths and Social Science, in both Tamil and English medium, into one `books/` folder.
2. Pair the two mediums. The same chapter in both languages lets you line up each English term with its Tamil term.
3. Look at the last pages of each book. Most Samacheer Kalvi books end with a glossary (கலைச்சொற்கள் / Glossary) of English-Tamil term pairs. Confirm this per book. Also check whether the Tamil-medium chapters give the English term in brackets after bold Tamil words, since that adds more pairs.
4. Extract text with `pdftotext`. Some Tamil PDFs use legacy fonts, so the output can be garbled. If a book gives no pairs or unreadable Tamil, run OCR with Tesseract's `tam` language data on that book.
5. Parse the pairs, lowercase the English side, merge duplicates, and add them to your existing glossary JSON with `"ok": false` on every new entry. Existing entries are never overwritten.
6. Spot-check about 10% of entries against the book pages. Fix the parser if one pattern fails, then rerun.
7. Add short English and Tamil meanings (`en_def`, `ta_def`) for the most frequent terms first. Textbook glossaries usually give term pairs only, so breadth (term pairs for everything) comes before depth (meanings for the top few hundred).
8. Ship `glossary.json` inside the repo. Lookup is in memory, so it costs almost nothing on a Pi and works fully offline.

**Starter extraction script** (run on your laptop, since it needs the PDFs and `pdftotext`; adjust the regex after you look at one real glossary page):

```python
import re, json, sys, subprocess
from pathlib import Path

def txt(pdf):
    r = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True)
    return r.stdout

def pairs(s):
    out = {}
    pat = r"^\s*([A-Za-z][A-Za-z \-]+?)\s{2,}([\u0B80-\u0BFF][\u0B80-\u0BFF \-]+)\s*$"
    for ln in s.splitlines():
        m = re.match(pat, ln)
        if m:
            out[m.group(1).strip().lower()] = m.group(2).strip()
    return out

def build(d, gl):
    for p in sorted(Path(d).glob("*.pdf")):
        pr = pairs(txt(p))
        if not pr:
            print("no pairs, check encoding or run ocr:", p.name)
        for en, ta in pr.items():
            gl.setdefault(en, {"ta": ta, "src": p.name, "ok": False})
    return gl

if __name__ == "__main__":
    out = Path(sys.argv[2])
    gl = {}
    if out.exists():
        with open(out, encoding="utf-8") as f:
            gl = json.load(f)
    gl = build(sys.argv[1], gl)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(gl, f, ensure_ascii=False, indent=1)
    print(len(gl), "terms")
```

Point it at your existing glossary file, for example `python build_gl.py books/ glossary.json`. Existing entries are kept as they are, and only new terms are added. Check the term count after each run, and read the "no pairs" lines to see which books need OCR.

**Handling gaps**
- Support plurals and simple variants ("vapours", "degrees").
- Log every passage term that is missing, so you can add it later.
- Keep the `ok` flag per entry so you can track which Tamil terms a teacher or you have checked. Your existing verified seed terms can be set to `"ok": true`.

### 3.6 Tamil output sections
Make these Tamil-first, built from templates plus glossary:
- Section headings (already bilingual)
- Quiz: question stem in English with the key term shown in Tamil beside it
- Hard words: the full table above
- Optional: a Tamil one-line gist per summary point, only for sentences whose key terms are all in the glossary

---

## 4. Performance and telemetry

Current run: 29.016 s, 402 tokens, 13.85 tok/s, peak RSS 1937.8 MiB, model 1083.33 MiB, on an i7-1185G7 laptop.

- Report the host honestly. "Laptop, not Raspberry Pi" is correct; add a line on expected Pi behaviour only once measured.
- Break timing into: model load, prefill, time to first token, decode, total. A single 29 s number hides what is slow.
- Cap `max_new_tokens` per section (summary, quiz, example) instead of one large generation.
- Reuse the shared prompt prefix across the two passes if the runtime allows it.
- Peak RSS of about 1.9 GB is workable on an 8 GB Pi but tight on 4 GB. State the Pi model you target.
- Set thread count explicitly and report it.

### Offline proof
- The telemetry showed `wlp0s20f3=UP`, default route active and `Offline status: ONLINE`.
- Re-run with wifi disabled (or airplane mode) and capture telemetry showing no active default route.
- Keep both captures in the repo so the claim can be checked.

---

## 5. Project and submission improvements

- **Barrier story:** one sentence on the barrier (Tamil-medium Class 8-10 students cannot get an understandable explanation of a hard passage without internet or a tutor), one on the learner group, one on how StudyAid addresses it.
- **Concrete impact example:** walk one student through the temperature passage, from hard sentence to simple sentence to Tamil term to quiz.
- **Generalisation test:** run at least 3 more passages (a biology one, a maths one, a physics one with numbers) and save the outputs. The organiser passage will not be this one.
- **Failure handling:** every section should degrade gracefully. If the quiz fails, fall back. If a glossary term is missing, say so.
- **Repo hygiene:** one-command run script, pinned requirements, a `glossary/` folder, sample outputs, a README with run steps and the telemetry captures.
- **Pi readiness:** document the aarch64 build steps and any ExecuTorch flags you used, so the finals team can reproduce quickly.

---

## 6. Priority order

| Priority | Item |
|---|---|
| P0 | Quiz always returns 3 valid questions |
| P0 | Bilingual glossary with correct definitions; remove "English only" |
| P0 | Build `glossary.json` from the Class 8-10 Samacheer Kalvi PDFs (term pairs first) |
| P0 | Offline telemetry capture with wifi off |
| P1 | Replace village example with the topic-matched bank |
| P1 | Simplified sentence keeps the triple-point meaning; number check |
| P1 | 3-point cited summary |
| P1 | Timing breakdown (load, prefill, decode) |
| P2 | Better readability metrics |
| P2 | Meanings (`en_def`, `ta_def`) for the top few hundred terms |
| P2 | Tests on 3+ other passages, repo cleanup |

---

## 7. How the work is run: orchestrator, parallel sub-agents, verifier

### 7.0 Work on the existing StudyAid project, not a rewrite

Everything in this file is meant to be applied to the project files you have already built (the ExecuTorch Python pipeline, the two-pass prompting, the telemetry code, the existing glossary JSON and the evidence report). Nothing here starts a new project. I have not seen those files, so the orchestrator does this first:

1. **Audit:** read the repo and write a short map of which file does what (model loading, prompts, simplify, summary, quiz, glossary, telemetry, report) and which stream in 7.2 touches which file.
2. **Baseline:** save the current output on the temperature passage (the run in section 1) as `baseline/`. Keep the existing real ExecuTorch run, model, two-pass prompting and telemetry working throughout.
3. **Edit in place:** each sub-agent changes the existing modules in its own area and adds new files only where nothing exists yet (for example the example bank). No renaming or reorganising the repo unless the orchestrator approves it.
4. **Isolation:** each sub-agent works on its own local branch or git worktree of the existing repo, so two agents never edit the same file at once. The orchestrator merges them locally one by one. If two streams need the same file, the orchestrator assigns it to one owner.
5. **Regression check:** the verifier compares every merged build with `baseline/`. Things that worked before (real ExecuTorch run, token and timing output, existing glossary terms, the evidence report numbers) must still work. Only the weaknesses in section 1 should change.
6. **Existing glossary file:** extend it, do not replace it. Your already verified seed terms stay with `"ok": true`, and new entries from the textbooks are added with `"ok": false`. If the existing JSON uses different keys from the schema in 3.2, the glossary agent adapts to the existing keys instead of changing every file that reads them.

### 7.1 Roles

| Role | Job | Writes code? |
|---|---|---|
| **Orchestrator** | Owns the plan and the task board, hands out work, tracks dependencies, merges finished streams, decides when a stage is done, and builds the final package | Only integration glue |
| **Sub-agents (parallel)** | Each owns one stream and one folder, and works only inside it | Yes, in their own folder |
| **Verifier** | Independent checker. Reads the spec and the outputs, runs the acceptance checks, and returns pass or fail with reasons. Does not fix anything and does not trust the builders' own claims | No feature code, only tests |

The verifier should start with fresh context and see only the spec, the interface contracts and the built output. That keeps it from inheriting a builder's blind spots.

### 7.2 Work streams

| Stream | Owns | Depends on |
|---|---|---|
| A. Glossary builder | `glossary.json` from the Samacheer Kalvi PDFs (section 3.5), OCR fallback, source notes | You downloading the PDFs |
| B. Quiz engine | Generate, validate, retry, deterministic fallback, multiple-choice distractors (section 2.5) | none |
| C. Simplifier and metrics | Two-sentence simplification, number-preservation check, readability metrics (2.3, 2.4) | none |
| D. Summary, examples, hard words | 3-point cited summary, local example bank, hard-word ranking (2.1, 2.6, 2.7) | A for ranking by glossary hit |
| E. Tamil rendering | Templates for headings and quiz stems, glossary lookup and output (section 3) | A |
| F. Telemetry and performance | Timing breakdown, offline capture, host label (section 4) | Integrated build |
| G. Packager | Judge package, README, evidence report (section 8) | All of the above |

A, B, C and D start in parallel. E starts once a first `glossary.json` exists. F runs only on the integrated build. G runs last.

### 7.3 Interface contracts first

Parallel agents collide when their outputs don't match. Before anything is built, the orchestrator fixes one JSON shape per stream and every agent writes to it. Example for the whole pipeline output:

```json
{
  "passage_id": "p1",
  "simple": ["The triple point of water is ...", "One kelvin is 1/273.16 of that temperature."],
  "summary": [{"txt": "Temperature measures how hot or cold something is.", "cite": ["S1"]}],
  "terms": [{"en": "absolute zero", "ta": "தனிச் சுழி வெப்பநிலை", "ok": false}],
  "quiz": [{"q": "...", "opts": ["...", "...", "...", "..."], "ans": 0, "cite": "S4"}],
  "example": {"id": "temp_chennai_ooty", "txt": "..."},
  "metrics": {"sents": [2, 2], "words": [30, 28]},
  "timing": {"load": 0.0, "prefill": 0.0, "decode": 0.0, "total": 0.0}
}
```

Each agent is told which keys it owns and must not touch the rest.

### 7.4 The loop

1. Orchestrator writes the plan, the contracts and the acceptance checks.
2. Sub-agents A to D build in parallel, each inside its own folder.
3. Verifier checks each stream on its own against its acceptance checks.
4. Failed streams go back to their owner with the verifier's reasons. Repeat until pass.
5. Orchestrator integrates (E, then the full pipeline) and the verifier checks the integrated build.
6. F measures performance and offline behaviour on the integrated build, run alone.
7. G builds the judge package and the verifier checks it from a clean copy.
8. You review the final product. Only after you confirm does anything go to git (section 9).

### 7.5 Verifier checklist

| Check | Pass condition |
|---|---|
| Quiz count | At least 3 questions on every test passage, each answer found in its cited sentence |
| Numbers kept | Every number in the original appears in the simplified text (for example 273.16) |
| Glossary correctness | No "English only" for a term that has an entry; regression tests for fahrenheit (32/212) and saturated |
| Examples | Example comes from the local bank, never from free generation |
| Tamil output | Renders properly, no garbled characters, headings and quiz stems in Tamil |
| Missing terms | A term with no entry is shown as "no Tamil entry", never invented |
| Offline | Run with wifi off: no default route, no network calls, `Offline status: OFFLINE` |
| Telemetry fields | Model, PTE size, peak RSS, load, prefill, decode, total, tokens, tokens/sec and host all present |
| Generalisation | Passes on at least 3 other passages (biology, maths, physics with numbers) |
| Clean run | Works from a fresh copy of the folder with the one-command run script |
| Glossary sampling | About 10% of extracted pairs checked against the book pages |

Do not tell the builders the exact test passages in advance, so the checks measure the pipeline and not the tests.

### 7.6 Running agents in parallel on one laptop

- The model run needs about 1.9 GB RAM and uses the CPU heavily. Let at most 2 agents call the model at the same time, or put a simple queue in front of it.
- Stream F (timing) must run alone, with nothing else busy, or the numbers will be wrong.
- Agents that only parse PDFs, write templates or write tests don't need the model and can run freely.

---

## 8. Final product for the judges

Built by stream G and approved by the verifier. It lives in its own `final/` folder and contains:

| Item | Purpose |
|---|---|
| `run_demo.sh` | One command that processes the organiser passage and prints the full output in the terminal (this is enough per the problem statement) |
| `demo_output_offline.txt` | The same run captured with wifi off, showing the offline telemetry |
| `glossary.json` | The Samacheer Kalvi based bilingual glossary |
| `evidence_report` | Short report: barrier, learner group, how StudyAid addresses it, numbers (model, size, memory, inference time), one concrete example |
| `samples/` | Outputs for 3+ other passages, to show it is not tuned to one passage |
| `README.md` | Run steps, requirements, host notes (laptop now, Pi at the finals) |

Suggested 2-3 minute demo flow:
1. Show the hard sentence from the passage.
2. Run the demo offline and show the simple version, the Tamil terms and the quiz.
3. Show the telemetry: model, size, memory, inference time, offline status.
4. Close with the concrete impact example for a rural Tamil-medium Class 8-10 student.

---

## 9. Local first, push only after you confirm

- All building, testing and verifying happens on your laptop. Nothing goes to the remote while the work is in progress.
- Local commits are fine as checkpoints. To make an accidental push impossible, disable pushing on the remote: `git remote set-url --push origin no_push`.
- Release gate: the orchestrator marks the final product ready, the verifier passes it, you review it and say it is confirmed. Only then re-enable the push URL and push once.
- Before that first push, check that the repo does not contain model files or PDFs you shouldn't publish (the 1 GB model file, the downloaded textbook PDFs), and that the glossary entries keep their source notes.
