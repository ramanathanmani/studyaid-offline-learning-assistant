# StudyAid Benchmark Results

**Model:** Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8  
**Backend:** Real ExecuTorch  
**Runs per passage:** 3  
**Status:** ONLINE  

| Passage | Words | Latency (s) | Tokens | Tokens/s | Peak RSS (MiB) [Base] | Retries (Reasons) | Quizzes | Quiz Sup | Summary OK | Shorter | Village | Words Exp | Offline |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| optics | 84 | 38.01 (35.03-40.17) | 624 (624-624) | 16.48 (15.54-17.82) | 1903.7 (1903.7-1903.8) [19.8 (19.8-19.8)] | 5.0 (5.0-5.0) (quiz_guard: only 2/3 valid; short_rewrite_guard; missing_section: summary; village_guard; missing_section: words) | 2.0 | 3/6 | 3/3 | 3/3 | 3/3 | 12/15 | ONLINE |
| photosynthesis | 160 | 21.72 (21.20-22.00) | 288 (288-288) | 13.26 (13.09-13.59) | 1903.7 (1903.5-1903.8) [19.8 (19.7-19.8)] | 2.0 (2.0-2.0) (village_guard; missing_section: words) | 3.0 | 0/9 | 3/3 | 3/3 | 3/3 | 15/15 | ONLINE |
| circuits | 175 | 35.70 (34.08-38.38) | 473 (473-473) | 13.29 (12.33-13.88) | 1903.8 (1903.8-1903.9) [19.8 (19.7-19.8)] | 2.0 (2.0-2.0) (quiz_guard: only 1/3 valid; village_guard) | 1.0 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | ONLINE |
| digestion | 164 | 34.24 (32.42-37.34) | 529 (529-529) | 15.51 (14.17-16.31) | 1903.6 (1903.5-1903.8) [19.8 (19.8-19.8)] | 1.0 (1.0-1.0) (village_guard) | 4.0 | 3/12 | 3/3 | 3/3 | 3/3 | 3/15 | ONLINE |
| sound | 155 | 27.13 (25.73-29.81) | 369 (369-369) | 13.67 (12.38-14.34) | 1903.7 (1903.6-1903.8) [19.7 (19.7-19.8)] | 2.0 (2.0-2.0) (village_guard; missing_section: words) | 3.0 | 0/9 | 3/3 | 3/3 | 3/3 | 15/15 | ONLINE |
| optics_long | 152 | 26.61 (25.63-28.38) | 337 (337-337) | 12.69 (11.87-13.15) | 1903.7 (1903.4-1903.9) [19.8 (19.7-19.8)] | 2.0 (2.0-2.0) (village_guard; missing_section: words) | 3.0 | 0/9 | 3/3 | 3/3 | 3/3 | 15/15 | ONLINE |
| **Overall Mean** | **148.3** | **30.57 (21.20-40.17)** | **437 (288-624)** | **14.15 (11.87-17.82)** | **1903.7 (1903.4-1903.9) [19.8 (19.7-19.8)]** | **2.3 (1.0-5.0) (quiz_guard: only 1/3 valid; quiz_guard: only 2/3 valid; short_rewrite_guard; missing_section: summary; village_guard; missing_section: words; village_guard; village_guard; missing_section: words)** | **2.7** | **9/48** | **18/18** | **18/18** | **18/18** | **75/90** | **ONLINE** |

