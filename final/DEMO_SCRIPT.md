# StudyAid: 2-3 Minute Judge Walkthrough & Demo Script

## Overview
This walkthrough demonstrates StudyAid running a 100% local, offline GenAI pipeline on a Raspberry Pi 5 / Edge device for a Class 9 Tamil-medium student under the Tamil Nadu Samacheer Kalvi state curriculum.

---

## 1. The Student Persona (30 seconds)
- **Speaker:** 
  > *"Meet Meena, a Class 9 student in rural Tamil Nadu studying in Tamil medium. After school, during a power cut with no Wi-Fi or mobile data, she struggles with dense English science textbooks. She has no tutor and cannot search online. StudyAid brings an offline AI tutor directly into her home on a low-cost Raspberry Pi 5 edge device."*
- **Action:** Point to the top persona banner on screen. Clarify that Meena is a labeled fictional persona representing the real challenges of rural students.

---

## 2. Zero-Network Verification (20 seconds)
- **Speaker:**
  > *"Notice the green status chip in the top header: 'Works Offline / இணையம் இன்றி இயங்கும்'. The device routing table has zero default route—Ethernet and Wi-Fi are fully disabled. Notice the device badge: 'Live on Raspberry Pi 5' (or Laptop Run). All inference, formatting, and fonts run completely locally from flash storage."*
- **Action:** Point at the `#offline-chip` and `#device-badge`.

---

## 3. The One-Click Sample Action (30 seconds)
- **Speaker:**
  > *"To test a standard textbook passage, Meena or the judges can click the golden 'Paste Sample Passage' button."*
- **Action:** Click **"✨ மாதிரி பத்தி ஒட்டு (Paste Sample Passage)"**.
- **Observation:** The textarea is instantly populated with the standard Class 9 Physics paragraph on Heat & Temperature:
  > *"Temperature is a physical quantity that expresses the degree of hotness or coldness of a substance. The SI unit of temperature is Kelvin (K). In everyday life, temperature is commonly measured in degrees Celsius (°C) or Fahrenheit (°F). Absolute zero is 0 K or -273.15 °C. Heat is energy in transit..."*
- **Speaker:**
  > *"Now we tap 'எளிதாக்கு / Make it easier'."*
- **Action:** Click the primary action button **"⚡ எளிதாக்கு (Make it easier)"**.
- **Observation:** The live progress spinner appears with real elapsed seconds counting live (`elapsed_s`).

---

## 4. Student Results Journey (60 seconds)
Once processing completes, show the 5 educational cards in order:

1. **Sentence Breakdown:**
   - Show how the passage is broken into numbered sentences `[S1]`, `[S2]`, `[S3]`.
   - Point out that the hardest sentence is highlighted in yellow and labeled *"கடின வாக்கியம் / Hardest Sentence"*.

2. **Simplified Rewrite (Exact Number Preservation):**
   - Point to the side-by-side comparison:
     - Original: *"Absolute zero is 0 K or -273.15 °C."*
     - Simple: *"Absolute zero is 0 K or -273.15 °C."*
   - Highlight: Scientific numbers are never lost or hallucinated.

3. **Key Summary Points:**
   - 3 concise, grounded points.
   - Click a citation badge like `[S1]` or `[S2]` to show instant smooth scrolling and highlighting of the source sentence in the reading view!

4. **Bilingual Scientific Glossary:**
   - Show the table: English Term (`temperature`, `kelvin`), exact Tamil translation (`வெப்பநிலை`, `கெல்வின்`), and textbook definitions from `glossary.json`.
   - Reiterate rule: *The LLM never invents Tamil text; all definitions come deterministically from the Class 9 glossary.*

5. **Everyday Context Example:**
   - Show the local rural familiar metaphor (e.g. stainless steel spoon in a tea tumbler or bullock cart mud physics).

6. **Interactive Quiz & Instant Pedagogical Feedback:**
   - Answer Question 1 correctly: Green checkmark appears with *✓ சரியான விடை! (Supported by [S1])*.
   - Answer Question 2 incorrectly on purpose: Red indicator shows the chosen option crossed out, reveals the correct answer, and immediately highlights the cited sentence in the reading view!
   - Complete all 3 questions to display the final score banner: *🎯 Final Quiz Score: 3 / 3 correct*.

---

## 5. The Judge Panel (30 seconds)
- **Speaker:**
  > *"Finally, for technical verification, let's open the Judge Panel."*
- **Action:** Click the top-right button **"⚖️ For Judges"**.
- **Demonstration:**
  - **Hardware & Telemetry:** Host (Raspberry Pi 5 ARM64), Model (SpinQuant INT4 PTE, 1.13 GB), 4 CPU cores, Route table (`OFFLINE`).
  - **Inference Timing:** Peak RSS ~1.6 GB, measured latency.
  - **Release Gate Score:** Laptop Hold-out Strict Pass: **100.0%** (interval [94.3%, 100.0%]), Mean weighted score: **100.0 / 100**.
  - **Limitations Disclaimer:** *Automatic scores measure grounding and zero number hallucination; human pedagogical check is verified in gold.csv.*

---

## 6. Closing (10 seconds)
- **Speaker:**
  > *"StudyAid proves that cutting-edge 1B INT4 models can run offline on a sub-$100 Raspberry Pi 5 to give rural students personalized, high-quality bilingual education with zero internet requirement."*
