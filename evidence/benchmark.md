# StudyAid Benchmark Results

**Model:** Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8  
**Backend:** Real ExecuTorch  
**Runs per passage:** 3  
**Status:** OFFLINE  

| Passage | Words | Latency (s) | Tokens | Tokens/s | Peak RSS (MiB) [Base] | Retries (Reasons) | Quizzes | Model Cite | Quiz Sup | Summary OK | Shorter | Village | Words Exp | Offline |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| optics | 84 | 37.49 (36.54-38.76) | 624 (624-624) | 16.66 (16.10-17.08) | 1903.4 (1903.3-1903.5) [19.7 (19.6-19.8)] | 5.0 (5.0-5.0) (quiz_guard: only 2/3 valid; short_rewrite_guard; missing_section: summary; village_guard; missing_section: words) | 2.0 | 0/6 | 3/6 | 3/3 | 3/3 | 3/3 | 12/15 | OFFLINE |
| photosynthesis | 160 | 21.81 (21.17-22.68) | 288 (288-288) | 13.22 (12.70-13.60) | 1903.7 (1903.7-1903.8) [19.8 (19.7-19.8)] | 2.0 (2.0-2.0) (village_guard; missing_section: words) | 3.0 | 0/9 | 0/9 | 3/3 | 3/3 | 3/3 | 15/15 | OFFLINE |
| circuits | 175 | 31.45 (31.07-32.10) | 473 (473-473) | 15.05 (14.74-15.23) | 1903.4 (1903.3-1903.5) [19.7 (19.7-19.8)] | 2.0 (2.0-2.0) (quiz_guard: only 1/3 valid; village_guard) | 1.0 | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | OFFLINE |
| digestion | 164 | 33.07 (32.59-33.92) | 529 (529-529) | 16.00 (15.59-16.23) | 1903.6 (1903.4-1903.8) [19.7 (19.7-19.8)] | 1.0 (1.0-1.0) (village_guard) | 4.0 | 0/12 | 3/12 | 3/3 | 3/3 | 3/3 | 3/15 | OFFLINE |
| sound | 155 | 28.64 (27.96-29.30) | 369 (369-369) | 12.89 (12.59-13.20) | 1903.5 (1903.4-1903.6) [19.8 (19.8-19.8)] | 2.0 (2.0-2.0) (village_guard; missing_section: words) | 3.0 | 0/9 | 0/9 | 3/3 | 3/3 | 3/3 | 15/15 | OFFLINE |
| optics_long | 152 | 31.54 (31.03-32.27) | 337 (337-337) | 10.69 (10.44-10.86) | 1903.5 (1903.4-1903.6) [19.7 (19.6-19.8)] | 2.0 (2.0-2.0) (village_guard; missing_section: words) | 3.0 | 0/9 | 0/9 | 3/3 | 3/3 | 3/3 | 15/15 | OFFLINE |
| **Overall Mean** | **148.3** | **30.66 (21.17-38.76)** | **437 (288-624)** | **14.08 (10.44-17.08)** | **1903.5 (1903.3-1903.8) [19.7 (19.6-19.8)]** | **2.3 (1.0-5.0)** | **2.7** | **0/48** | **9/48** | **18/18** | **18/18** | **18/18** | **75/90** | **OFFLINE** |

