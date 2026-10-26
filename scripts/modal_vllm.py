"""Serve an open-weight model on Modal through vLLM's OpenAI-compatible API, for the second-family arms.

Deploy: ``modal deploy scripts/modal_vllm.py``. The endpoint checks the key in the Modal secret
``collusion-vllm`` (``VLLM_API_KEY``); the adapter reads the same key and the URL from ``.env``
(``OPENWEIGHT_API_KEY``, ``OPENWEIGHT_BASE_URL``). One container at most, shut down after 15 idle minutes.
"""

import subprocess

import modal

MODEL = "Qwen/Qwen3-32B"
REVISION = "9216db5781bf21249d130ec9da846c4624c16137"   # the weights every Qwen cell and verdict ran on (HF cache refs/main)
SERVED_NAME = "qwen3-32b"
PORT = 8000

image = (modal.Image.debian_slim(python_version="3.12")
         .uv_pip_install("vllm==0.11.0", "huggingface_hub[hf_transfer]==0.35.3")
         .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"}))
weights = modal.Volume.from_name("collusion-hf-cache", create_if_missing=True)
compiled = modal.Volume.from_name("collusion-vllm-cache", create_if_missing=True)
app = modal.App("collusion-openweight")


@app.function(image=image, gpu="H100", timeout=60 * 60, scaledown_window=15 * 60, max_containers=1,
              secrets=[modal.Secret.from_name("collusion-vllm")],
              volumes={"/root/.cache/huggingface": weights, "/root/.cache/vllm": compiled})
@modal.concurrent(max_inputs=8)
@modal.web_server(port=PORT, startup_timeout=20 * 60)
def serve() -> None:
    subprocess.Popen(["vllm", "serve", MODEL, "--revision", REVISION, "--served-model-name", SERVED_NAME, "--host", "0.0.0.0",
                      "--port", str(PORT), "--max-model-len", "16384", "--enable-auto-tool-choice",
                      "--tool-call-parser", "hermes", "--reasoning-parser", "qwen3", "--uvicorn-log-level", "warning"])
