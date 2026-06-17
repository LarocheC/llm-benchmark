# Results

Versioned snapshots of benchmark runs. **Absolute resolve rates on small/clustered
slices are sanity signals, not leaderboard-comparable numbers** — a representative or
full-set run is required for that.

---

## calib-v1 — 2026-06-17 — SWE-bench Verified, representative random sample

- **Sample:** `--sample-shuffle 42 --limit N` → a reproducible random sample across all repos
  (django, sphinx, sympy, pytest, scikit-learn, xarray…). Much more representative than calib-v0's
  astropy-clustered first-8. Frontier models ran **n=50**; local models ran the first **n=20** of the
  same shuffled order (a clean subset → within-tier comparisons are apples-to-apples).
- **Harness:** Inspect AI 0.3.240 `inspect_evals/swe_bench` (react agent), Docker sandbox; `--message-limit 60`, `--max-tokens 64000`.
- **Azure GPT-5.4 / mini:** Responses API, `background=false`, `reasoning_effort=medium`. Hit 429 rate-limit
  storms at 16 concurrent; fixed by raising the deployment TPM quota + per-model concurrency (Azure 12, local 1).
- **Local:** Devstral-Small-2 / Mistral-Small via Ollama, `num_ctx 32768`, single-stream.

| Model | Type | n | Resolved | Resolve % | Tokens |
|---|---|---|---|---|---|
| `openai/azure/gpt-5.4` | frontier API | 50 | 38 | **76.0%** | 17.7M |
| `openai/azure/gpt-5.4-mini` | frontier API | 50 | 36 | **72.0%** | 20.6M |
| `ollama/devstral-small-2` (specialist) | local 24B | 20 | 7 | **35.0%** | 7.9M |
| `ollama/mistral-small` (generalist) | local 24B | 20 | 2 | **10.0%** | 3.7M |

**Takeaways**
- **gpt-5.4 = 76% lands in the published frontier range → harness is calibrated.** (calib-v0's noisy 50% on 8 clustered tasks was just small-sample noise.)
- **gpt-5.4 vs gpt-5.4-mini: 76% vs 72% — not separable at n=50** (binomial CI ≈ ±12%). Mini is ~as capable here at far lower price, and spent *more* tokens. Real separation needs larger n + multiple seeds.
- **Specialist ≫ generalist (same 24B class): 35% vs 10% (3.5×).** The generalist also improved from 0% (calib-v0, tiny context) to 10% via the 32K context bump — context matters, but agentic-coding specialization is the bigger lever.
- Discriminating spread overall: **frontier 72–76% › local specialist 35% › local generalist 10%.**
- Qualitative (transcript analysis of `django-14672`): the specialist wins via better **orientation** (uses the real filesystem vs a hallucinated path), **precise fix localization** (`identity()` vs `__init__`), and **self-verification** (runs tests before submitting); the generalist submitted an unverified, plausible-but-wrong patch.

**Caveats / next**
- Frontier n=50, local n=20 → cross-tier comparison is approximate; within-tier (same shuffled instances) is exact.
- For leaderboard-grade numbers and to separate gpt-5.4 from mini: larger sample (100–200), ≥5 seeds, bootstrap CIs.

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
