import os
import sys
import time
import argparse
import ctypes
import psutil

def load_libs():
    try:
        import executorch
        pkg_dir = list(executorch.__path__)[0]
        sos = [
            'lib/libexecutorch.so',
            'lib/libexecutorch_threadpool.so',
            'lib/libexecutorch_backend_xnnpack.so',
            'lib/libexecutorch_kernels_optimized.so',
            'lib/libexecutorch_kernels_quantized.so',
            'extension/llm/custom_ops/libcustom_ops_aot_lib.so',
        ]
        for s in sos:
            p = os.path.join(pkg_dir, s)
            if os.path.exists(p):
                ctypes.CDLL(p, mode=ctypes.RTLD_GLOBAL)
    except Exception as e:
        sys.exit(f"Failed to load ExecuTorch libraries: {e}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pte", default="models/llama1b/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte")
    p.add_argument("--tokenizer", default="models/llama1b/tokenizer.model")
    args = p.parse_args()

    if not os.path.exists(args.pte):
        sys.exit(f"PTE file not found: {args.pte}")
    if not os.path.exists(args.tokenizer):
        sys.exit(f"Tokenizer not found: {args.tokenizer}")

    load_libs()

    try:
        from executorch.extension.llm.runner import TextLLMRunner, GenerationConfig
    except ImportError as e:
        sys.exit(f"Failed to import TextLLMRunner: {e}")

    t0 = time.perf_counter()
    try:
        runner = TextLLMRunner(model_path=args.pte, tokenizer_path=args.tokenizer)
    except Exception as e:
        sys.exit(f"Failed to initialize TextLLMRunner: {e}")
    load_dt = time.perf_counter() - t0

    cfg = GenerationConfig()
    cfg.max_new_tokens = 80
    cfg.temperature = 0.0
    cfg.echo = False

    toks = []
    pmt = "Explain in one sentence why a pencil looks bent in a glass of water."
    t1 = time.perf_counter()
    try:
        runner.generate(prompt=pmt, config=cfg, token_callback=lambda t: toks.append(t))
    except Exception as e:
        sys.exit(f"Failed during text generation: {e}")
    gen_dt = time.perf_counter() - t1

    resp = "".join(toks).strip()
    n_tok = len(toks)
    tps = round(n_tok / gen_dt, 2) if gen_dt > 0 else 0.0
    pte_sz = os.path.getsize(args.pte)
    rss_mb = round(psutil.Process().memory_info().rss / (1024 * 1024), 2)

    print("=== SMOKE TEST OUTPUT ===")
    print(f"Reply: {resp}")
    print(f"Tokens generated: {n_tok}")
    print(f"Generation time: {gen_dt:.3f} s")
    print(f"Tokens per second: {tps}")
    print(f"Load time: {load_dt:.3f} s")
    print(f"PTE size: {pte_sz} bytes ({pte_sz / (1024 * 1024):.2f} MB)")
    print(f"Peak RSS: {rss_mb} MB")

if __name__ == "__main__":
    main()
