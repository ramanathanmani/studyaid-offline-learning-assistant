import os
import sys
import argparse
import time
import tomllib
from studyaid.backend import MockBackend, ETBackend
from studyaid.gloss import load_gl
from studyaid.pipeline import run_pipeline
from studyaid.telem import collect_telem, get_net_state, get_host_info
from studyaid.render import render_all

def load_cfg(cfg_path):
    if os.path.exists(cfg_path):
        with open(cfg_path, "rb") as f:
            return tomllib.load(f)
    return {}

def check_offline_cmd():
    net = get_net_state()
    host = get_host_info()
    print("=== OFFLINE STATUS CHECK ===")
    print(host["host_label"])
    print(f"OS: {host['os']}")
    print(f"Inspection method: {net.get('method')}")
    print("Interfaces:")
    for it in net.get("ifaces", []):
        print(f"  {it['name']}: {it['state']}")
    print(f"Default route active: {'YES' if net.get('has_def_route') else 'NO'}")
    if net.get("is_offline"):
        print("Verdict: OFFLINE")
    else:
        active = [f"{it['name']}={it['state']}" for it in net.get("ifaces", []) if it["name"] != "lo" and it["state"] != "DOWN"]
        act_str = ", ".join(active) if active else "none"
        def_str = "YES" if net.get("has_def_route") else "NO"
        print(f"Verdict: ONLINE (active interfaces: {act_str}, default route: {def_str})")

def run_cmd(args):
    cfg = load_cfg(args.config)
    m_cfg = cfg.get("model", {})
    r_cfg = cfg.get("runtime", {})

    if args.require_offline:
        net = get_net_state()
        if not net.get("is_offline"):
            active = [f"{it['name']}={it['state']}" for it in net.get("ifaces", []) if it["name"] != "lo" and it["state"] != "DOWN"]
            act_str = ", ".join(active) if active else "none"
            def_str = "YES" if net.get("has_def_route") else "NO"
            sys.exit(f"Error: system is ONLINE (active interfaces: {act_str}, default route: {def_str}). Offline required by --require-offline.")

    pass_p = args.passage or r_cfg.get("passage", "samples/optics.txt")
    if not os.path.exists(pass_p):
        sys.exit(f"Passage file not found: {pass_p}")

    with open(pass_p, "r", encoding="utf-8") as f:
        pass_txt = f.read()

    w_cnt = len(pass_txt.split())
    if w_cnt < 150 or w_cnt > 300:
        print(f"Warning: passage word count ({w_cnt}) is outside the recommended 150-300 word range.\n", file=sys.stderr)

    gl_p = args.glossary or "data/tamil_glossary.json"
    gl = load_gl(gl_p) if os.path.exists(gl_p) else {}

    is_mock = args.mock or r_cfg.get("mock", False)
    pte_p = args.pte or m_cfg.get("pte", "")
    tok_p = args.tokenizer or m_cfg.get("tokenizer", "")
    m_name = m_cfg.get("name", "Llama-3.2-1B-Instruct")
    max_new = int(m_cfg.get("max_new", 320))
    p1_max = int(m_cfg.get("max_new_pass1", 320))
    p2_max = int(m_cfg.get("max_new_pass2", 220))
    two_pass = args.two_pass if args.two_pass is not None else m_cfg.get("two_pass", True)

    if is_mock or not pte_p:
        bk = MockBackend()
    else:
        bk = ETBackend(pte_p, tok_p)

    t0 = time.perf_counter()
    pipe_res = run_pipeline(pass_txt, bk, gl, max_new=max_new, max_new_p1=p1_max, max_new_p2=p2_max, two_pass=two_pass)
    inf_time = time.perf_counter() - t0

    telem_res = collect_telem(
        m_name=m_name,
        pte_path=pte_p,
        tok_cnt=pipe_res["tok_cnt"],
        inf_time=inf_time,
        is_mock=getattr(bk, "is_mock", False)
    )

    rep, txt_p, json_p = render_all(pipe_res, telem_res, out_dir=args.out_dir)
    print(rep)
    print(f"\n[Saved outputs]:\n  Text: {txt_p}\n  JSON: {json_p}")

def main():
    p = argparse.ArgumentParser(prog="studyaid", description="Offline Study Aid for Rural Tamil Nadu")
    sub = p.add_subparsers(dest="cmd", required=True)

    r_p = sub.add_parser("run")
    r_p.add_argument("--passage", default=None)
    r_p.add_argument("--pte", default=None)
    r_p.add_argument("--tokenizer", default=None)
    r_p.add_argument("--two-pass", action="store_true", default=None)
    r_p.add_argument("--mock", action="store_true", default=False)
    r_p.add_argument("--config", default="config.toml")
    r_p.add_argument("--glossary", default="data/tamil_glossary.json")
    r_p.add_argument("--out-dir", default="outputs")
    r_p.add_argument("--require-offline", action="store_true", default=False)

    sub.add_parser("check-offline")

    args = p.parse_args()
    if args.cmd == "run":
        run_cmd(args)
    elif args.cmd == "check-offline":
        check_offline_cmd()

if __name__ == "__main__":
    main()
