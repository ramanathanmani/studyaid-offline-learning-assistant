import os
import re
import ctypes

def load_et_libs():
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
    except Exception:
        pass

class MockBackend:
    def __init__(self):
        self.is_mock = True
        self.name = "MockBackend"

    def gen(self, prompt, max_new=480):
        p_low = prompt.lower()
        if "rewrite in fewer words" in p_low:
            txt = "<SIMPLE>Light bends at a slant.</SIMPLE>"
        elif "summary of the main scientific points" in p_low or "summary of the passage" in p_low:
            txt = "<SUMMARY>Light bends when it passes between different transparent media. Its speed alters across different optical densities.</SUMMARY>"
        elif "words to explain" in p_low:
            txt = "<WORDS>\nrefraction | bending of light\nmedium | substance\nnormal | perpendicular line\nobliquely | at a slant\n</WORDS>"
        elif "village-life example" in p_low:
            txt = "<VILLAGE>In a village near Thanjavur, farmer Murugan pulls a wooden plow across wet paddy fields. The thick mud causes the plow path to undergo deviation.</VILLAGE>"
        elif "quiz questions" in p_low or ("<quiz>" in p_low and "<simple>" not in p_low):
            txt = (
                "<QUIZ>\n"
                "Q: What causes refraction to occur?\n"
                "A: velocity difference in different media\n"
                "C: S3\n\n"
                "Q: What is the deviation of a ray of light called?\n"
                "A: refraction\n"
                "C: S2\n\n"
                "Q: How does the refracted ray bend when entering a rarer medium from a denser medium?\n"
                "A: bent away from the normal\n"
                "C: S5\n\n"
                "Q: How does light travel through a uniform optical medium?\n"
                "A: in straight lines\n"
                "C: S1\n"
                "</QUIZ>"
            )
        else:
            txt = (
                "<SIMPLE>When light enters water or glass at a slant, its path bends.</SIMPLE>\n"
                "<SUMMARY>Light bends when it passes from one clear material to another at an angle. This bending happens because light travels at different speeds in different materials.</SUMMARY>\n"
                "<VILLAGE>When a bullock cart travels from a smooth road into mud, the path of travel undergoes deviation and the cart is bent away from the normal straight line.</VILLAGE>\n"
                "<WORDS>\n"
                "refraction | bending of light\n"
                "medium | substance light travels through\n"
                "normal | perpendicular line\n"
                "obliquely | at an angle\n"
                "transparent | clear substance\n"
                "</WORDS>"
            )
        tok_cnt = len(txt.split())
        return txt, tok_cnt

class ETBackend:
    def __init__(self, pte_path, tok_path):
        self.is_mock = False
        self.name = "Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8"
        self.pte_path = pte_path
        self.tok_path = tok_path
        
        if not pte_path or not os.path.exists(pte_path):
            raise FileNotFoundError(
                f"ExecuTorch model file (.pte) not found at: '{pte_path}'. "
                "Provide model path via --pte <path> or config.toml."
            )
            
        if not tok_path or not os.path.exists(tok_path):
            raise FileNotFoundError(
                f"Tokenizer file not found at: '{tok_path}'. "
                "Provide tokenizer path via --tokenizer <path> or config.toml."
            )

        load_et_libs()

        try:
            from executorch.extension.llm.runner import TextLLMRunner, GenerationConfig
            self._cfg_cls = GenerationConfig
            self.runner = TextLLMRunner(model_path=pte_path, tokenizer_path=tok_path)
        except ImportError as err:
            raise RuntimeError(
                "ExecuTorch Python runtime is not installed or runner is missing. "
                "Install ExecuTorch or run with --mock for offline testing."
            ) from err

    def gen(self, prompt, max_new=480):
        self.runner.reset()
        cfg = self._cfg_cls()
        cfg.max_new_tokens = max_new
        cfg.temperature = 0.0
        cfg.echo = False
        toks = []
        self.runner.generate(prompt=prompt, config=cfg, token_callback=lambda t: toks.append(t))
        clean = "".join(toks).replace("<|eot_id|>", "").replace("<|end_of_text|>", "").strip()
        if prompt.endswith("<SIMPLE>") and not clean.startswith("<SIMPLE>"):
            clean = "<SIMPLE>" + clean
        elif prompt.endswith("<QUIZ>\nQ:") and not clean.startswith("<QUIZ>"):
            clean = "<QUIZ>\nQ:" + clean
        n_tok = len(toks)
        return clean, n_tok
