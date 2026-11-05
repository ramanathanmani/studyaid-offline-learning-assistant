import os
import re

class MockBackend:
    def __init__(self):
        self.is_mock = True
        self.name = "MockBackend"

    def gen(self, prompt, max_new=480):
        if "pass 2" in prompt.lower() or "only the quiz" in prompt.lower():
            txt = (
                "<QUIZ>\n"
                "Q: What causes refraction to occur?\n"
                "A: difference in the velocity of light in different media\n"
                "C: S3\n"
                "Q: What is the deviation of a ray of light called?\n"
                "A: deviation of ray of light is called refraction\n"
                "C: S2\n"
                "Q: How does the refracted ray bend when entering a rarer medium from a denser medium?\n"
                "A: refracted ray is bent away from the normal\n"
                "C: S5\n"
                "</QUIZ>"
            )
        elif "pass 1" in prompt.lower() or "do not include quiz" in prompt.lower():
            txt = (
                "<SIMPLE>When light enters water or glass at a slant, its path bends.</SIMPLE>\n"
                "<SUMMARY>Light bends when it passes from one clear material to another at an angle. This bending happens because light travels at different speeds in different materials. When light goes from water or glass into air, it bends away from the straight vertical line.</SUMMARY>\n"
                "<VILLAGE>Think of walking a bullock cart from a smooth tar road into a muddy field at an angle. As the first wheel hits the thick mud, it slows down while the other wheel on the tar road is still moving fast. This difference in speed makes the entire cart turn or bend off its straight path. In the same way, a ray of light slows down and bends when it enters water from air.</VILLAGE>\n"
                "<WORDS>\n"
                "deviation | bending or turning away from a straight line\n"
                "interface | boundary surface where two materials meet\n"
                "medium | material through which light travels\n"
                "obliquely | at a slant or angle\n"
                "refraction | the bending of light as it moves between materials\n"
                "transparent | see-through material that allows light to pass\n"
                "velocity | speed in a given direction\n"
                "</WORDS>"
            )
        else:
            txt = (
                "<SIMPLE>When light enters water or glass at a slant, its path bends.</SIMPLE>\n"
                "<SUMMARY>Light bends when it passes from one clear material to another at an angle. This bending happens because light travels at different speeds in different materials. When light goes from water or glass into air, it bends away from the straight vertical line.</SUMMARY>\n"
                "<VILLAGE>Think of walking a bullock cart from a smooth tar road into a muddy field at an angle. As the first wheel hits the thick mud, it slows down while the other wheel on the tar road is still moving fast. This difference in speed makes the entire cart turn or bend off its straight path. In the same way, a ray of light slows down and bends when it enters water from air.</VILLAGE>\n"
                "<WORDS>\n"
                "deviation | bending or turning away from a straight line\n"
                "interface | boundary surface where two materials meet\n"
                "medium | material through which light travels\n"
                "obliquely | at a slant or angle\n"
                "refraction | the bending of light as it moves between materials\n"
                "transparent | see-through material that allows light to pass\n"
                "velocity | speed in a given direction\n"
                "</WORDS>\n"
                "<QUIZ>\n"
                "Q: What causes refraction to occur?\n"
                "A: difference in the velocity of light in different media\n"
                "C: S3\n"
                "Q: What is the deviation of a ray of light called?\n"
                "A: deviation of ray of light is called refraction\n"
                "C: S2\n"
                "Q: How does the refracted ray bend when entering a rarer medium from a denser medium?\n"
                "A: refracted ray is bent away from the normal\n"
                "C: S5\n"
                "</QUIZ>"
            )
        n_tok = len(txt.split())
        return txt, n_tok

class ETBackend:
    def __init__(self, pte_path, tok_path):
        self.is_mock = False
        self.name = "ExecuTorch-Llama3.2-1B"
        self.pte_path = pte_path
        self.tok_path = tok_path
        
        if not pte_path or not os.path.exists(pte_path):
            raise FileNotFoundError(
                f"ExecuTorch model file (.pte) not found at: '{pte_path}'. "
                "Export Llama 3.2 1B Instruct using scripts/export_model.sh and provide via --pte <path>, "
                "or run with --mock for offline test mode."
            )
            
        if not tok_path or not os.path.exists(tok_path):
            raise FileNotFoundError(
                f"Tokenizer file not found at: '{tok_path}'. "
                "Provide tokenizer path via --tokenizer <path>, or run with --mock for offline test mode."
            )

        try:
            from executorch.extension.llm.runner import TextLLMRunner, GenerationConfig
            self._cfg_cls = GenerationConfig
            self.runner = TextLLMRunner(model_path=pte_path, tokenizer_path=tok_path)
        except ImportError:
            try:
                from examples.models.llama.runner.runner import Runner
                self._cfg_cls = None
                self.runner = Runner(model_path=pte_path, tokenizer_path=tok_path)
            except ImportError as err:
                raise RuntimeError(
                    "ExecuTorch Python runtime is not installed or bindings are missing. "
                    "Install ExecuTorch or run with --mock for offline testing."
                ) from err

    def gen(self, prompt, max_new=480):
        if hasattr(self.runner, "generate"):
            if self._cfg_cls:
                cfg = self._cfg_cls(max_new_tokens=max_new, temperature=0.2)
                res = self.runner.generate(prompt, config=cfg)
            else:
                res = self.runner.generate(prompt, max_seq_len=max_new)
            n_tok = getattr(self.runner, "last_tokens_generated", len(str(res).split()))
            return str(res), int(n_tok)
        raise RuntimeError("ExecuTorch runner does not have a supported generate method.")
