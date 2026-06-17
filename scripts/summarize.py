#!/usr/bin/env python3
"""Summarize SWE-bench eval logs: resolve rate + token usage per run.

Seeds the cost-normalized scoring step. Defensive across inspect_ai versions;
for authoritative, interactive detail use `uv run inspect view`.

  uv run python scripts/summarize.py [LOG_DIR]   # default: ./logs
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    try:
        from inspect_ai.log import list_eval_logs, read_eval_log
    except Exception as e:  # pragma: no cover
        sys.exit(f"inspect_ai not importable ({e}). Run: uv sync")

    log_dir = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "logs")
    logs = list_eval_logs(log_dir)
    if not logs:
        sys.exit(f"No .eval logs under {log_dir}. Run a sweep first.")

    rows = []
    for info in logs:
        try:
            log = read_eval_log(info)
        except Exception as e:
            print(f"skip {info}: {e}")
            continue

        model = getattr(getattr(log, "eval", None), "model", "?")
        n = rate = None
        try:
            res = log.results
            n = getattr(res, "completed_samples", None) or getattr(res, "total_samples", None)
            for score in getattr(res, "scores", []) or []:
                metrics = getattr(score, "metrics", {}) or {}
                for mname in ("accuracy", "mean"):
                    if mname in metrics:
                        rate = getattr(metrics[mname], "value", None)
                        break
                if rate is not None:
                    break
        except Exception:
            pass

        in_tok = out_tok = tot_tok = 0
        try:
            for u in (getattr(log.stats, "model_usage", {}) or {}).values():
                in_tok += getattr(u, "input_tokens", 0) or 0
                out_tok += getattr(u, "output_tokens", 0) or 0
                tot_tok += getattr(u, "total_tokens", 0) or 0
        except Exception:
            pass

        rows.append((str(model), n, rate, in_tok, out_tok, tot_tok))

    hdr = f"{'model':42} {'n':>4} {'resolve':>8} {'in_tok':>11} {'out_tok':>11} {'tot_tok':>11}"
    print(hdr)
    print("-" * len(hdr))
    for model, n, rate, i, o, t in rows:
        rstr = f"{rate * 100:.1f}%" if isinstance(rate, (int, float)) else "?"
        print(f"{model[:42]:42} {str(n if n is not None else '?'):>4} {rstr:>8} {i:>11,} {o:>11,} {t:>11,}")
    print("\nResolve = mean all-or-nothing score (every FAIL_TO_PASS + PASS_TO_PASS test green).")
    print("Cost-normalized scoring: divide resolve by $/run once you attach per-token pricing.")


if __name__ == "__main__":
    main()
