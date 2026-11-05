from studyaid.telem import get_net_state, get_host_info, get_peak_rss_mb, collect_telem

def test_get_net_state():
    net = get_net_state()
    assert "ifaces" in net
    assert "has_def_route" in net
    assert "is_offline" in net
    assert isinstance(net["ifaces"], list)

def test_get_host_info():
    host = get_host_info()
    assert "host_label" in host
    assert ("HOST: laptop" in host["host_label"] or "HOST: Raspberry Pi" in host["host_label"])
    assert "cores" in host
    assert host["cores"] >= 1
    assert "ram_gb" in host
    assert host["ram_gb"] > 0

def test_get_peak_rss_mb():
    rss = get_peak_rss_mb()
    assert isinstance(rss, float)
    assert rss > 0.0

def test_collect_telem():
    telem = collect_telem("TestModel", None, 150, 2.5, is_mock=True)
    assert telem["model_name"] == "TestModel"
    assert telem["tok_cnt"] == 150
    assert telem["inf_time_sec"] == 2.5
    assert telem["is_mock"] is True
    assert telem["pte_size_mb"] is None
