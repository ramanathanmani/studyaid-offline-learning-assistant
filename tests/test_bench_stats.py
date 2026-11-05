import glob
import json
from scripts.bench import compute_benchmark_stats

def test_compute_benchmark_stats():
    runs = [
        {
            "passage": "optics",
            "words": 84,
            "inf_time_sec": 38.0,
            "tokens": 600,
            "tok_per_sec": 15.0,
            "peak_rss_mib": 1850.0,
            "baseline_rss_mib": 45.0,
            "retries": 1,
            "quiz_count": 3,
            "summary_ok": True,
            "guards": {
                "quiz_supported_cnt": 2,
                "quiz_total_cnt": 3,
                "rewrite_shorter": True,
                "village_relevant": True,
                "words_explained_cnt": 3,
                "words_cand_cnt": 5
            },
            "p1_retried": True,
            "p1_retry_reason": "short_rewrite_guard",
            "p2_retried": False,
            "p2_retry_reason": "none",
            "offline_status": "OFFLINE",
            "pipeline": {"quiz": [1, 2, 3]}
        },
        {
            "passage": "optics",
            "words": 84,
            "inf_time_sec": 40.0,
            "tokens": 620,
            "tok_per_sec": 15.5,
            "peak_rss_mib": 1860.0,
            "baseline_rss_mib": 45.0,
            "retries": 0,
            "quiz_count": 3,
            "summary_ok": True,
            "guards": {
                "quiz_supported_cnt": 3,
                "quiz_total_cnt": 3,
                "rewrite_shorter": True,
                "village_relevant": True,
                "words_explained_cnt": 4,
                "words_cand_cnt": 5
            },
            "p1_retried": False,
            "p1_retry_reason": "none",
            "p2_retried": False,
            "p2_retry_reason": "none",
            "offline_status": "OFFLINE",
            "pipeline": {"quiz": [1, 2, 3]}
        },
        {
            "passage": "photosynthesis",
            "words": 160,
            "inf_time_sec": 35.0,
            "tokens": 500,
            "tok_per_sec": 14.0,
            "peak_rss_mib": 1880.0,
            "baseline_rss_mib": 46.0,
            "retries": 0,
            "quiz_count": 3,
            "summary_ok": False,
            "guards": {
                "quiz_supported_cnt": 2,
                "quiz_total_cnt": 3,
                "rewrite_shorter": True,
                "village_relevant": True,
                "words_explained_cnt": 2,
                "words_cand_cnt": 4
            },
            "p1_retried": False,
            "p1_retry_reason": "none",
            "p2_retried": False,
            "p2_retry_reason": "none",
            "offline_status": "OFFLINE",
            "pipeline": {"quiz": [1, 2, 3]}
        }
    ]
    
    res = compute_benchmark_stats(runs, m_name="TestModel", runs_per_p=2)
    assert len(res["summary"]) == 2
    
    opt = res["summary"][0]
    assert opt["passage"] == "optics"
    assert opt["words"] == 84
    assert opt["inf_time_mean"] == 39.0
    assert opt["tokens_mean"] == 610
    assert opt["rss_mean"] == 1855.0
    assert opt["base_rss_mean"] == 45.0
    assert opt["quiz_sup"] == "5/6"
    assert opt["offline_status"] == "OFFLINE"
    
    ov = res["overall"]
    assert ov["passage"] == "Overall Mean"
    expected_words = round((84 + 160) / 2, 1)
    assert ov["words"] == expected_words
    assert ov["offline_status"] == "OFFLINE"

def test_six_passages_words_mean():
    passage_words = [84, 160, 175, 164, 155, 152]
    mean_val = round(sum(passage_words) / len(passage_words), 1)
    assert mean_val == 148.3
