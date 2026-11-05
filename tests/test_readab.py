from studyaid.readab import sent_stats, compare_readab

def test_exact_readability_numbers():
    s_orig = "When a ray of light travels from one transparent medium into another obliquely, the path of the light undergoes deviation."
    s_simp = "When light enters water or glass at a slant, its path bends."
    
    st_orig = sent_stats(s_orig)
    assert st_orig["w_cnt"] == 20
    assert st_orig["l_cnt"] == 101
    assert st_orig["avg_l"] == 5.05
    
    st_simp = sent_stats(s_simp)
    assert st_simp["w_cnt"] == 12
    assert st_simp["l_cnt"] == 47
    assert st_simp["avg_l"] == 3.92
    
    comp = compare_readab(s_orig, s_simp)
    assert comp["diff"]["w_chg"] == -40.0
    assert comp["diff"]["l_chg"] == -53.5
    assert comp["diff"]["avg_chg"] == -22.4
