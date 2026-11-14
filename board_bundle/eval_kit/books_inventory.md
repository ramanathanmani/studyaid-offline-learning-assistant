# StudyAid Finals - Textbook Inventory & Scout Report

**Report Date:** 2026-11-14  
**Agent:** BOOK SCOUT Agent  
**Target Class:** Class 9 (Tamil Nadu State Board Curriculum)  
**Curriculum Scope:** Science, Social Science, Mathematics (Term 1 / Full Year)  
**Source Directory:** `/home/rock/Downloads/Class 9 Books/`  
**Target Directories:**  
- Primary: `/home/rock/.gemini/antigravity/scratch/studyaid/eval_kit/books/`  
- Secondary Pack: `/home/rock/Downloads/studyaid_finals_pack/eval_kit/books/`

---

## 1. Executive Summary

A comprehensive scout inspection was conducted across all textbook PDF resources provided in the source repository. Six core textbooks were identified, categorized, verified, and safely mirrored into the target `eval_kit/books/` structures without altering or moving any original source assets.

### Key Highlights:
- **Completeness:** 100% textbook twin coverage achieved. All three key subjects (Mathematics, Science, Social Science) have both English (`en`) and Tamil (`ta`) editions present and accounted for (3 matched pairs, 6 books total).
- **Naming Standardization:** All assets have been standardized to the canonical pattern `CLASS_SUBJECT_TERM_LANG.pdf` (`9_sci_1_en.pdf`, `9_sci_1_ta.pdf`, `9_soc_1_en.pdf`, `9_soc_1_ta.pdf`, `9_math_1_en.pdf`, `9_math_1_ta.pdf`).
- **Integrity Verification:** 100% byte-for-byte and MD5 cryptographic match verified across all primary and mirrored secondary destinations.
- **Linguistic & Ingestion Analysis:**
  - **English Textbooks (`en`):** Outstanding text extraction cleanliness via standard PDF text extractors (`pdftotext` / poppler). Ready for immediate vector ingestion and LLM parsing.
  - **Tamil Textbooks (`ta`):** Tamil text is recognized and extracts rich Unicode Tamil content (87.9% – 97.4% Tamil character share). However, poppler reports font ligature parsing warnings (`tm_ma_halant`, `tm_c_ikaar`, `tm_pa_halant`) resulting in doubled pulli markers and isolated `U+FFFD` replacement glyphs. StudyAid's ingestion pipeline must apply regex ligature normalization or OCR fallback for optimal indexing.

---

## 2. Master Textbook Inventory

| Source Path | New Name | Language | Subject | Term | Page Count | Extraction Quality | Twin Status | Notes / Flags |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `/home/rock/Downloads/Class 9 Books/English Version/Class_9_Science_English_2024_Edition-www.tntextbooks.in.pdf` | `9_sci_1_en.pdf` | `en` | `sci` | `1` | 328 | Clean | Matched twin found (`9_sci_1_ta.pdf`) | 2024 Edition. Clean text, high-resolution figures. |
| `/home/rock/Downloads/Class 9 Books/Tamil Version/Class_9_Science_Tamil_2024_edition-www.tntextbooks.in.pdf` | `9_sci_1_ta.pdf` | `ta` | `sci` | `1` | 336 | Garbled Ligatures / Needs Normalization | Matched twin found (`9_sci_1_en.pdf`) | 2024 Edition. 95.7% Tamil content; InDesign font ligature artifacts (`tm_ma_halant`). |
| `/home/rock/Downloads/Class 9 Books/English Version/Class_9_Social_Science_English_2025_Edition-www.tntextbooks.in.pdf` | `9_soc_1_en.pdf` | `en` | `soc` | `1` | 328 | Clean | Matched twin found (`9_soc_1_ta.pdf`) | 2025 Edition. Pristine text and map/diagram labels. |
| `/home/rock/Downloads/Class 9 Books/Tamil Version/Class_9_Social_Science_Tamil_2025_Edition-www.tntextbooks.in.pdf` | `9_soc_1_ta.pdf` | `ta` | `soc` | `1` | 344 | Garbled Ligatures / Needs Normalization | Matched twin found (`9_soc_1_en.pdf`) | 2025 Edition. 97.4% Tamil content; high frequency of decomposed vowel marks (`போ`, `ொ`). |
| `/home/rock/Downloads/Class 9 Books/English Version/Class_9_Mathematics_English_2025_Edition-www.tntextbooks.in.pdf` | `9_math_1_en.pdf` | `en` | `math` | `1` | 328 | Clean | Matched twin found (`9_math_1_ta.pdf`) | 2025 Edition. Clean English text; contains introductory Tamil Thirukkural on p. 5. |
| `/home/rock/Downloads/Class 9 Books/Tamil Version/Class_9_Mathematics_Tamil_2025_Edition-www.tntextbooks.in.pdf` | `9_math_1_ta.pdf` | `ta` | `math` | `1` | 344 | Garbled Ligatures / Needs Normalization | Matched twin found (`9_math_1_en.pdf`) | 2025 Edition. 87.9% Tamil content (remainder math notation/English terms). Double-pulli artifacts present. |

---

## 3. Linguistic Verification & Character Distribution

Language classification was verified algorithmically by extracting text across sample ranges (pages 5–20) as well as the full documents, measuring Unicode character codepoints in the Tamil range (`U+0B80` to `U+0BFF`) against ASCII Latin alphabetic characters (`A-Z`, `a-z`).

### Quantitative Language Breakdown:
- **English Science (`9_sci_1_en.pdf`):**
  - Sample (pp. 5–20): 28,024 Latin letters, 0 Tamil characters (0.00% Tamil).
  - Full Document: 583,655 Latin letters, 2,675 Tamil characters (marginal preface/glossary references). Confirmed English.
- **English Social Science (`9_soc_1_en.pdf`):**
  - Sample (pp. 5–20): 25,985 Latin letters, 0 Tamil characters (0.00% Tamil).
  - Full Document: 587,732 Latin letters, 1,141 Tamil characters. Confirmed English.
- **English Mathematics (`9_math_1_en.pdf`):**
  - Sample (pp. 5–20): 14,775 Latin letters, 70 Tamil characters (0.47% Tamil).
  - *Linguistic Note:* Page 5 contains the traditional Tamil couplet from Thirukkural: *"எண்ணென்ப ஏனை எழுத்தென்ப இவ்விரண்டும் கண்ணென்ப வாழும் உயிர்க்கு"*, followed immediately by its English translation.
  - Full Document: 271,044 Latin letters, 2,735 Tamil characters. Confirmed English.
- **Tamil Science (`9_sci_1_ta.pdf`):**
  - Sample (pp. 5–20): 31,571 Tamil characters, 1,413 Latin letters (95.72% Tamil share).
  - Full Document: 675,941 Tamil characters, 30,704 Latin characters. Confirmed Tamil.
- **Tamil Social Science (`9_soc_1_ta.pdf`):**
  - Sample (pp. 5–20): 37,358 Tamil characters, 1,006 Latin letters (97.38% Tamil share).
  - Full Document: 751,931 Tamil characters, 30,810 Latin characters. Confirmed Tamil.
- **Tamil Mathematics (`9_math_1_ta.pdf`):**
  - Sample (pp. 5–20): 16,073 Tamil characters, 2,211 Latin letters (87.91% Tamil share).
  - Full Document: 316,991 Tamil characters, 38,302 Latin characters (higher English proportion due to algebraic variable names, theorem identifiers, and dual-language glossary entries like `is not equal to`, `Natural numbers`). Confirmed Tamil.

---

## 4. Extraction Cleanliness & OCR Readiness Analysis

### A. English Edition Textbooks
- **Extraction Behavior:** `pdftotext` runs cleanly without emitting syntax warnings to `stderr`.
- **Formatting & Layout:** Running text, unit titles, learning objectives, and practice exercises extract with clear spacing and intact punctuation.
- **Mathematical Formulae:** In `9_math_1_en.pdf`, inline arithmetic and basic algebraic expressions extract legibly, though multi-tier fractions and radical signs use poppler typographical approximations (e.g., standard backtick/parenthesis blocks).
- **Ingestion Recommendation:** Direct text extraction via poppler / PDF parser is production-ready.

### B. Tamil Edition Textbooks
- **Extraction Warnings:** Poppler outputs syntax warnings during font parsing:
  ```text
  Syntax Warning: Could not parse ligature component "tm" of "tm_ma_halant" in parseCharName
  Syntax Warning: Could not parse ligature component "tm" of "tm_c_ikaar" in parseCharName
  Syntax Warning: Could not parse ligature component "tm" of "tm_pa_halant" in parseCharName
  ```
- **Nature of Artifacts:**
  1. **Double Pulli (`U+0BCD` duplicated):** Words with pure consonants (mei ezhuthukkal) frequently have two successive viramas (`்்`), e.g., `எண்்ணத்`, `நீங்்கள்`, `இல்்லலை`, `கிடைத்்த`.
  2. **Decomposed/Corrupted Compound Vowels:** Compound vowel combinations using kombu (`ெ`, `ே`, `ை`, `ொ`, `ோ`) sometimes decouple or introduce the Unicode replacement character `\ufffd`, e.g., `நோோக்்க`, `சொொற்்களையும்`. Total `\ufffd` counts across entire books: Science (1,498), Social Science (7,565), Math (2,853).
- **Ingestion Pipeline Recommendation:**
  - **Option 1 (Fast & Effective):** Apply a lightweight Tamil text normalization regex step during chunk preprocessing:
    - Replace `\u0BCD\u0BCD+` with `\u0BCD`.
    - Strip rogue `\uFFFD` where flanked by valid consonant-vowel combinations.
    - Normalize decomposed Tamil unicode sequences using Python's `unicodedata.normalize('NFC', text)`.
  - **Option 2 (High-Fidelity OCR):** For evaluation questions targeting complex Tamil questions or historical sources in Social Science, pass page renders through Tesseract OCR (with `tam` language pack) or Google Cloud Vision API to capture 100% clean ligatures.

---

## 5. Twin Pairing Status

All 3 subject tracks have valid, matched twin textbooks across both language streams:

| Subject | English Edition (`en`) | Tamil Edition (`ta`) | Alignment Status | Page Count Comparison |
| :--- | :--- | :--- | :---: | :---: |
| **Science** | `9_sci_1_en.pdf` | `9_sci_1_ta.pdf` | **Matched Pair** | 328 pages (EN) vs 336 pages (TA) |
| **Social Science** | `9_soc_1_en.pdf` | `9_soc_1_ta.pdf` | **Matched Pair** | 328 pages (EN) vs 344 pages (TA) |
| **Mathematics** | `9_math_1_en.pdf` | `9_math_1_ta.pdf` | **Matched Pair** | 328 pages (EN) vs 344 pages (TA) |

*Observation on Page Counts:* The Tamil editions contain 8 to 16 additional pages compared to their English counterparts due to script font metrics, wider glyph spacing, and Tamil-specific appendices. Chapter unit sequences and curricula are fully mirrored.

---

## 6. Cryptographic File Integrity & Storage Audit

All target files were verified against their original source files. Byte sizes and MD5 checksums match with zero discrepancies. Original source files remain completely untouched and unmodified.

| Target File Name | File Size (Bytes) | MD5 Checksum | Copied Destinations Verified |
| :--- | :---: | :---: | :---: |
| `9_sci_1_en.pdf` | 42,682,176 | `fa61a8af4e548fa0646c10813cb245c6` | Scratch & Finals Pack (`eval_kit/books/`) |
| `9_soc_1_en.pdf` | 19,216,215 | `963996431ec5e94b2ebffcb6873528b8` | Scratch & Finals Pack (`eval_kit/books/`) |
| `9_math_1_en.pdf` | 28,314,750 | `ad41f8a21849a60e6573c0048e77c8e9` | Scratch & Finals Pack (`eval_kit/books/`) |
| `9_sci_1_ta.pdf` | 44,252,459 | `979aa75c3d256860ce3970b15b3c5453` | Scratch & Finals Pack (`eval_kit/books/`) |
| `9_soc_1_ta.pdf` | 31,122,132 | `6e085600c4ecdfb776a91176bc5da940` | Scratch & Finals Pack (`eval_kit/books/`) |
| `9_math_1_ta.pdf` | 27,552,418 | `04004986358c2e68be415fceaa431c17` | Scratch & Finals Pack (`eval_kit/books/`) |

---

## 7. Non-Book Files & Duplicate Audit

- No extraneous files, auxiliary downloads, `.DS_Store`, thumbs, or corrupt partial downloads were found in `/home/rock/Downloads/Class 9 Books/` or its subdirectories.
- Exactly 6 files exist in source folders, representing 3 complete textbook pairs.
- No files were moved or deleted from source folders.
