#!/usr/bin/env bash
# OPTIONAL: serve a HF model locally via vLLM as an OpenAI-compatible server.
# Requires:  uv add vllm   (multi-GB; needs NVIDIA GPU + CUDA — you have an RTX 4090).
# A 24 GB 4090 fits ~8B in fp16; use --quantization awq/gptq for larger models.
#
# After it's up, point models.yaml at:  openai-api/local/<model>
# with LOCAL_BASE_URL=http://localhost:8000/v1 and LOCAL_API_KEY=dummy-key in .env.
set -euo pipefail
MODEL="${1:-meta-llama/Meta-Llama-3-8B-Instruct}"
exec uv run vllm serve "$MODEL" \
  --port 8000 --seed 0 \
  --gpu-memory-utilization 0.85 \
  --api-key dummy-key
