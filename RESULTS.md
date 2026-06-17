# Results

Versioned snapshots of benchmark runs. **Absolute resolve rates on small/clustered
slices are sanity signals, not leaderboard-comparable numbers** — a representative or
full-set run is required for that.

---

## calib-v0 — 2026-06-17 — SWE-bench Verified, first 8 instances

- **Harness:** Inspect AI 0.3.240, `inspect_evals/swe_bench` (default `react` agent), Docker sandbox.
- **Slice:** `--limit 8` → the first 8 Verified instances (all `astropy__*`). n=8, repo-clustered ⇒ std≈0.53, wide CI. **Not leaderboard-comparable.**
- **Common flags:** `--message-limit 60`, `--max-tokens 64000`, `--temperature 0` (auto-dropped for reasoning models), `--fail-on-error 0.2`.
- **Azure GPT-5.4 / mini:** Responses API, `background=false`, `reasoning_effort=medium`.
- **Local:** `mistral-small:24b` via Ollama, `emulate_tools=true`.

| Model | Resolved | Resolve % | Wall time | Total tokens (cached) | Cost |
|---|---|---|---|---|---|
| `openai/azure/gpt-5.4` | 4/8 | 50% | 8m51s | 2.75M (1.73M CR) | ~$3–4 |
| `openai/azure/gpt-5.4-mini` | 4/8 | 50% | 11m04s | 3.35M (2.70M CR) | <$1 |
| `ollama/mistral-small:24b` (local) | 0/8 | 0% | 24m18s | 727K | $0 |

**Takeaways**
- Harness discriminates (frontier 50% vs local 0%) and emits real per-instance scores — full pipeline (patch → apply → FAIL_TO_PASS/PASS_TO_PASS → score) confirmed across providers.
- gpt-5.4 vs mini are not separable at n=8 on this clustered slice — needs a larger representative sample.
- **Reproduce:** `uv run python scripts/run_sweep.py --limit 8` then `uv run python scripts/summarize.py logs`.

**Known caveats / next**
- First-N is alphabetical (astropy-heavy) — for a real calibration use a representative random sample of Verified, ≥5 seeds, and report bootstrap CIs.
- `gpt-5.4-pro` deployment is parked (background-only, slow + ~12× cost; ill-suited to multi-turn agents).
