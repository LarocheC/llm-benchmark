# LLM Coding Benchmark

A benchmark harness for comparing **LLMs** (and, later, **LLM coding agents**) on hard
coding tasks.

This repo currently contains **v0: the reuse loop** — running **SWE-bench Verified** through
[Inspect AI](https://inspect.aisi.org.uk/)'s `inspect_evals` against any provider, to *validate
the harness* before we invest in hand-authored tasks. It supports **Azure AI Foundry** API models
and **local self-hosted** models out of the box; the eval command is identical across providers —
**only `--model` changes.**

## Why this shape

- **Model-under-test first.** One frozen, minimal scaffold; identical task/prompt/budgets for every
  model, so score deltas are attributable to the model. The harness moves scores far more than the
  model does, so a single agentic run can't fairly compare both at once — pick one axis. We pick the
  model.
- **Agent-under-test later, for free.** The task + grader don't care who produced the patch. When we
  want an agent leaderboard, we keep the same tasks and swap only the solver
  (`SOLVER=pkg/agent ... run_sweep.py`) — a second leaderboard over the same set, not a fork.
- **Reuse for validation, hand-author for ranking.** Public benchmarks (incl. SWE-bench Verified) are
  in training corpora, so their absolute scores are a contaminated upper bound. Here Verified is the
  **calibration + plumbing check** (does our resolve rate match the public leaderboard?). The
  *official* ranking will come later from a private, hand-authored split.

## Layout

```
pyproject.toml        uv project (deps pinned via uv.lock)
.env.example          provider credentials template (cp -> .env)
models.yaml           the sweep: list of {model string, env} — the only thing that changes per model
scripts/
  preflight.py        readiness check (runs WITHOUT credentials)
  run_sweep.py        loop models.yaml -> `inspect eval`, per-model logs
  summarize.py        resolve rate + token usage per run (cost-normalized scoring seed)
  smoke.sh            one-model 5-instance smoke run
  serve_local_vllm.sh optional: serve a HF model via vLLM (OpenAI-compatible)
logs/                 eval outputs (gitignored; view with `inspect view`)
```

## Install

```bash
uv sync                              # creates .venv, installs + locks deps
uv run python scripts/preflight.py   # what's ready / what to fill in (no creds needed)
```

System requirements (verified): **Docker** running (default sandbox); **~30 GiB disk** for the full
500 Verified images; **HuggingFace + ghcr.io** network access. Authenticate to pull Epoch AI's
pre-built instance images:

```bash
gh auth token | docker login ghcr.io -u <github-username> --password-stdin
```

## Configure providers

`cp .env.example .env` and fill in only what you use. **Azure has four distinct paths** — the
`--model` prefix *and* the base-URL suffix differ:

| Provider | `--model` string | Key env vars | Base URL |
|---|---|---|---|
| Azure GPT (Azure OpenAI) | `openai/azure/<deployment>` | `AZUREAI_OPENAI_API_KEY`, `AZUREAI_OPENAI_BASE_URL`, `AZUREAI_OPENAI_API_VERSION` | **no** `/models` |
| Azure Llama/Phi/generic | `azureai/<deployment>` | `AZURE_API_KEY` (or `AZUREAI_API_KEY`), `AZUREAI_BASE_URL` | **ends in** `/models` |
| Azure Mistral | `mistral/azure/<deployment>` | `AZUREAI_MISTRAL_API_KEY`, `AZUREAI_MISTRAL_BASE_URL` | **ends in** `/models` |
| Azure Claude | `anthropic/azure/<deployment>` | `AZUREAI_ANTHROPIC_API_KEY`, `AZUREAI_ANTHROPIC_BASE_URL` | **ends in** `/models` |
| **Local — Ollama** | `ollama/<model>` | `OLLAMA_BASE_URL` (optional) | server at `:11434` |
| **Local — generic OpenAI-API** | `openai-api/local/<model>` | `LOCAL_BASE_URL`, `LOCAL_API_KEY` | your server |
| **Local — vLLM native** | `vllm/<hf-id>` | `VLLM_BASE_URL`, `VLLM_API_KEY` | needs `uv add vllm` |

**Keyless / Entra ID (Azure):** install is already done (`azure-identity`); run `az login` (or assign
a managed identity) and **leave the matching `*_API_KEY` unset**. Audience via `AZUREAI_AUDIENCE`.

**Local on this box:** Ollama is already installed — `ollama serve`, then `ollama pull llama3.1`.
A small local model will resolve ~0% of SWE-bench tasks; that's expected and still validates the loop
mechanically. For the resolve-rate *ballpark* check, use a strong Azure model. For bigger local
models, serve via vLLM (`scripts/serve_local_vllm.sh`) and use the `openai-api/local/...` row.

## Run

```bash
# Smoke a single model (5 instances) — proves the plumbing
scripts/smoke.sh ollama/llama3.1 -M emulate_tools=true
scripts/smoke.sh openai/azure/<your-gpt-deployment>

# Sweep every enabled model in models.yaml (5 instances each by default)
uv run python scripts/run_sweep.py
uv run python scripts/run_sweep.py --only azure-gpt        # one model
uv run python scripts/run_sweep.py --dry-run               # show commands only
uv run python scripts/run_sweep.py --limit none            # full 500-instance run

# Look at results
uv run inspect view                            # interactive web log viewer
uv run python scripts/summarize.py             # resolve rate + token table
```

## Validation criterion (does the harness work?)

1. Run ~10 instances with a **known-capable** model (e.g. a GPT-4o-class Azure deployment).
2. `uv run inspect view` — confirm each sample ran, applied a patch, and got scored. Scoring is
   **all-or-nothing**: `1.0` iff every FAIL_TO_PASS *and* every PASS_TO_PASS test passes. Samples
   with sandbox/parse errors are *harness* issues, not model misses.
3. **Ballpark:** the resolve rate should land near the published SWE-bench Verified figure for that
   model class. **~0% on a strong model ⇒ a plumbing bug** (wrong base-URL suffix, missing tool
   calling, patch not applied) — not real performance.
4. For leaderboard parity, export with `save_outputs_to_swebench_format()` and rescore with the
   official `swebench` harness (known Inspect↔official divergences tracked upstream).

Each run records per-sample **token usage** (and cost for major providers) in the `.eval` log — that's
the input to cost-normalized scoring later. `vllm/` / `openai-api/` log tokens but not `$`; supply
pricing externally.

## Reproducibility & gotchas

- **Pin everything.** `uv.lock` pins deps; pin `AZUREAI_OPENAI_API_VERSION` (its default drifts); pin
  the `inspect_evals` version (task defaults change between releases).
- `--temperature 0`. `--seed` only affects some providers (OpenAI/Google/Groq/Mistral/HF/vLLM) — **not**
  Anthropic/Azure/`openai-api`. For local determinism, serve via vLLM with `--seed 0`.
- **Don't exceed ~32 concurrent Docker containers** (`--max-samples`/`--max-connections`).
- **Tool calling:** the SWE-bench agent uses tools. Local/Ollama models often lack native tool-calling
  — pass `-M emulate_tools=true` (already set for the local entries in `models.yaml`).
- **Run ≥5 seeds and report confidence intervals** before trusting a gap between two models. (Statistical
  rigor comes in once the loop is green.)

## Roadmap

- **v0 (here):** reuse loop — SWE-bench Verified, multi-provider, plumbing validated.
- **v1:** hand-authored **private** task split (own task-contract: `meta.yaml` + pinned Dockerfile +
  gold `solution/` + `grader.py` + FAIL_TO_PASS/PASS_TO_PASS); add a LiveCodeBench date-window for a
  clean public signal; agent-under-test track via `--solver`.
- **v2:** GPU-kernel track on the RTX 4090 (reuse KernelBench's `fast_p` scorer, author our own
  Triton-GRU reference); multi-domain difficulty ladder.
