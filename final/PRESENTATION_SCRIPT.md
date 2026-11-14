# StudyAid: Judge & Stage Presentation Script
**Project:** StudyAid — Offline Smart Learning Assistant  
**Hardware Target:** Raspberry Pi 5 (Quad-Core Arm Cortex-A76, 8 GB RAM)  
**Target Syllabus:** Tamil Nadu State Board (Samacheer Kalvi) Class 9 Science & Mathematics  
**Format:** 3 to 5 Minutes Live Presentation + Interactive Edge Demo  

---

## Presentation Roadmap & Timing

| Scene | Section | Duration | Key Focus |
|---|---|---|---|
| **Scene 1** | The Hook: Meet Meena | 0:00 – 0:45 | Rural persona, language barrier, power cuts, no data |
| **Scene 2** | The Problem: Why Cloud AI Fails | 0:45 – 1:15 | Hallucinated formulas, non-standard Tamil, internet dependency |
| **Scene 3** | The Solution: StudyAid on Edge | 1:15 – 1:45 | 100% offline INT4 AI on sub-$80 Arm hardware |
| **Scene 4** | The Live Product Journey | 1:45 – 3:15 | Sample button, hardest sentence, simplification, glossary, quiz |
| **Scene 5** | Under the Hood: Arm & Architecture | 3:15 – 4:00 | Arm Cortex-A76, ExecuTorch, 10–12 tok/s, zero hallucination |
| **Scene 6** | The Technical Verdict & Impact | 4:00 – 4:45 | 100% strict pass rate on hold-out, air-gapped privacy, closing |

---

## Scene 1: The Hook — Meet Meena (0:00 – 0:45)

**[Visual Cue / Slide 1]:** *A photograph or illustration of Meena, a 14-year-old student in a rural Tamil Nadu government school uniform, studying by candlelight beside an open textbook.*

**Speaker:**
> "Judges, imagine a 14-year-old student named Meena. She lives in a rural village near Tirunelveli and studies in a government high school in Tamil medium.
>
> This year, she enters Class 9. For the first time, her science textbooks introduce dense academic English: terms like *'thermodynamic equilibrium'*, *'absolute zero'*, and *'fractional indices'*. 
>
> At 7:00 PM, a daily power cut hits her village. The local mobile tower loses power. She has no broadband, no mobile data, and her family cannot afford private tutoring. 
>
> When she gets stuck on a paragraph, she is completely on her own. Today, modern AI promises to transform education, but for students like Meena, cloud AI simply does not exist."

---

## Scene 2: The Problem — Why Cloud AI Fails (0:45 – 1:15)

**[Visual Cue / Slide 2]:** *Comparison split-screen: Cloud AI (Red X: \$20/mo subscription, 4G/5G required, hallucinated Tamil/numbers) vs. Edge AI (Green Check: 100% Offline, Zero data, Verified curriculum).*

**Speaker:**
> "Why can’t Meena just use ChatGPT or a cloud educational app?
> 
> Three fundamental barriers:
> 
> 1. **Zero Connectivity:** If the server is in the cloud, an air-gapped rural home cannot reach it.
> 2. **Linguistic Garbage:** Cloud models translate technical concepts into machine-translated, broken Tamil (*mojibake*) that does not match the Tamil Nadu government textbook syllabus.
> 3. **The Hallucination Danger:** In science, precision matters. When an LLM rounds $273.15\text{ }^\circ\text{C}$ to $273$ or invents formula terms, the student fails their state board exam.
>
> We needed a completely new approach: bringing modern GenAI directly onto edge hardware, with zero cloud dependency."

---

## Scene 3: The Solution — StudyAid on Edge (1:15 – 1:45)

**[Visual Cue / Slide 3]:** *Photograph of the physical Raspberry Pi 5 board mounted with power bank, labeled: 'StudyAid Edge Station — 5W Power, 100% Offline, Arm64 Native'.*

**Speaker:**
> "Enter **StudyAid**: an offline, on-device AI educational assistant designed specifically for Tamil Nadu Class 9 students.
>
> StudyAid runs entirely on a standard, sub-\$80 Raspberry Pi 5 powered by a quad-core **Arm Cortex-A76 processor**.
>
> It does not require Wi-Fi, Ethernet, or mobile data. It consumes under 7 Watts of power—meaning it can run for an entire evening off a small 5-volt power bank.
>
> Let us show you the real student product in action right now."

---

## Scene 4: The Live Product Journey (1:45 – 3:15)

**[Live Demo Action]:** *Switch screen to the live browser on `http://localhost:8080` (or `http://192.168.102.237:8080`).*

### 1. Zero-Network Verification
**Speaker:**
> "Look at the top header. Notice the green chip: **'Works Offline / இணையம் இன்றி இயங்கும்'**. 
>
> This is not a static graphic—the system inspects the Linux kernel route table in real time. Wi-Fi and Ethernet are disabled. There is zero default route. Everything you are about to see is running locally on device."

### 2. One-Click Sample Selection
**[Live Demo Action]:** *Click the golden **'✨ மாதிரி பத்தி ஒட்டு (Paste Sample Passage)'** button.*

**Speaker:**
> "A student or judge doesn't need to type lengthy text. With one click on the golden **'மாதிரி பத்தி ஒட்டு'** button, we load a dense passage from Class 9 Science Unit 7 on *Heat & Temperature*.
>
> Now, we tap the primary action: **'⚡ எளிதாக்கு (Make it easier)'**."

**[Live Demo Action]:** *Click **'⚡ எளிதாக்கு'**. The live timer starts counting seconds.*

**Speaker:**
> "Notice the live timer. We never fake progress bars. Our persistent INT4 model is running inference right now on the Arm cores."

### 3. The 5 Educational Cards
**[Live Demo Action]:** *Scroll through the generated student cards as inference finishes (~25s).*

**Speaker:**
> "Here is Meena’s learning journey:
>
> 1. **Reading View:** The text is parsed into numbered sentences. Sentence 1 is automatically flagged in bright yellow: *'கடின வாக்கியம் / This sentence is the hard one'*.
> 2. **Simplification with Number Preservation:** Look at the side-by-side comparison. The exact numbers—$0\text{ K}$, $-273.15\text{ }^\circ\text{C}$—are strictly preserved. Our deterministic guardrails ensure zero number hallucination.
> 3. **3 Key Summary Points:** Each summary point has a clickable badge—`[S1]`, `[S3]`, `[S5]`. Watch: when I tap `[S3]`, the reading view instantly scrolls and highlights the cited source sentence!
> 4. **Official Bilingual Glossary:** Here is *'temperature' -> வெப்பநிலை*, *'absolute zero' -> தனிச் சுழி வெப்பநிலை*. **Crucial rule:** The LLM is never allowed to hallucinate Tamil. All definitions are deterministically mapped to the verified Class 9 State Board glossary.
> 5. **Local Everyday Example:** A familiar rural Tamil Nadu metaphor—comparing temperature using May heat in Chennai ($40\text{ }^\circ\text{C}$), winter in Ooty ($15\text{ }^\circ\text{C}$), and a kitchen tea tumbler."

### 4. Interactive Quiz
**[Live Demo Action]:** *Answer Question 1 correctly (Green check). Answer Question 2 incorrectly on purpose (Red indicator).*

**Speaker:**
> "Finally, the comprehension quiz. 
> 
> When Meena answers Question 1 correctly, she gets instant positive reinforcement. 
> 
> If she answers Question 2 incorrectly—watch: it immediately flags the mistake and highlights the exact sentence in the textbook that proves the right answer! 
> 
> That is real pedagogical feedback, delivered with zero internet."

---

## Scene 5: Under the Hood — Arm & Model Architecture (3:15 – 4:00)

**[Live Demo Action]:** *Click top-right button **'⚖️ நடுவர் பகுதி / For Judges'** to open the technical telemetry drawer.*

**[Visual Cue / Slide 4]:** *Architecture diagram showing Arm Cortex-A76 -> SpinQuant INT4 ExecuTorch -> Python Supervisor -> Web UI.*

**Speaker:**
> "Judges, let's open the **Judge Panel** to look under the hood.
>
> * **Hardware:** Broadcom BCM2712 with Quad-Core **Arm Cortex-A76** 64-bit cores.
> * **Model Architecture:** Meta Llama-3.2-1B-Instruct quantized with **SpinQuant INT4**. The entire model is just **1.13 GB** (`1,135,951,488 bytes`), running on PyTorch's native **ExecuTorch runtime**.
> * **Memory Footprint:** Peak RSS is only **1.61 GB** on the Pi. That leaves over 6 GB of RAM free.
> * **Arm NEON Optimization:** We achieve **10 to 12.8 tokens per second** on pure CPU generation without any external NPU accelerator!
> * **Strict Pipeline Freeze:** The pipeline is frozen at git tag `finals-freeze` (`d53f824`). The web product communicates cleanly via a supervised, unbuffered IPC pipe."

---

## Scene 6: The Technical Verdict & Impact (4:00 – 4:45)

**[Visual Cue / Slide 5]:** *Final Summary Slide showing Eval Metrics (100% Strict Pass Rate, 30/30 Gold Sample Pass, Zero Hallucinations, Sub-\$80 Hardware).*

**Speaker:**
> "How do we know it actually works?
>
> * On our held-out test suite of 30 unseen textbook paragraphs, StudyAid achieved a **100.0% strict pass rate** across all automated checks: summary citations, readability improvement, glossary precision, and number integrity.
> * In our 30-sample human verification in `gold.csv`, zero hallucinations were detected.
> * Every single byte—including the Tamil font—is bundled locally under SIL Open Font License.
>
> **Closing:**
> StudyAid proves that by combining state-of-the-art **Arm edge hardware**, optimized **INT4 ExecuTorch quantization**, and strict **curricular guardrails**, we don't need a multi-million-dollar datacenter to empower students. 
>
> We can place a world-class, bilingual AI tutor into the hands of every student like Meena, anywhere in the world—even after the power goes out.
>
> Thank you. We welcome your questions."

---

## Quick Q&A Cheat-Sheet for Judges

| Likely Judge Question | Recommended Answer |
|---|---|
| **"Why not use an 8B or 70B model?"** | A 1B model in INT4 requires only 1.6 GB RAM and runs at 10–12 tok/s on a 5W Arm CPU. An 8B model would exceed edge RAM, generate massive heat, and take minutes per sentence. By constraining domain scope to Class 9 and using deterministic templates for Tamil, 1B outperforms 70B in speed, grounding, and reliability. |
| **"How do you prevent the LLM from making up Tamil words?"** | The LLM generates structured semantic tags (`<SIMPLE>`, `<SUMMARY>`, `<WORDS>`). The Python verification layer intersects extracted terms with the official Tamil Nadu State Board `glossary.json`. The model is *never* allowed to generate raw Tamil text directly. |
| **"What happens during a power cut?"** | The Raspberry Pi 5 runs on a standard 5V/5A USB-C power bank. It consumes ~5–7W during active inference and ~2.5W at idle, giving 6+ hours of uninterrupted study on a single \$15 power bank. |
| **"Why Raspberry Pi and Arm?"** | Arm Cortex-A76 cores offer the best performance-per-watt profile for edge compute. ExecuTorch’s NEON-accelerated CPU kernels deliver immediate interactive speeds without requiring expensive, power-hungry discrete GPUs. |
