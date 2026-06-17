#!/usr/bin/env bash
# Cheap 5-instance smoke run for ONE model — validates the harness end-to-end.
# Usage: scripts/smoke.sh <provider/model> [extra inspect flags...]
#   scripts/smoke.sh ollama/llama3.1 -M emulate_tools=true
#   scripts/smoke.sh openai/azure/my-gpt-deployment
set -euo pipefail
MODEL="${1:?usage: smoke.sh <provider/model> [extra inspect flags...]}"; shift || true
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a
exec inspect eval inspect_evals/swe_bench \
  --model "$MODEL" --limit 5 \
  --max-connections 8 --max-samples 8 --temperature 0 \
  --log-dir "logs/smoke" "$@"
