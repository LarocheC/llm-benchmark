#!/usr/bin/env python3
"""Run the SWE-bench Verified reuse loop across one or more models.

The eval command is identical across providers — only --model and that model's
env vars change. Config lives in models.yaml; secrets in .env.

  uv run python scripts/run_sweep.py                 # all enabled models
  uv run python scripts/run_sweep.py --only azure-gpt # just one
  uv run python scripts/run_sweep.py --limit none     # full 500-instance run
  uv run python scripts/run_sweep.py --dry-run        # print commands only
  SOLVER=my_pkg/my_agent uv run python scripts/run_sweep.py   # agent-under-test track
"""
from __future__ import annotations

import argparse
import os
import shlex
import string
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def expand(value, environ) -> str:
    if not isinstance(value, str):
        return value
    return string.Template(value).safe_substitute(environ)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run SWE-bench Verified across models from models.yaml")
    ap.add_argument("--config", default=str(ROOT / "models.yaml"))
    ap.add_argument("--only", help="comma-separated model names (overrides 'enabled' flags)")
    ap.add_argument("--limit", help="override defaults.limit (int, or 'none' for the full set)")
    ap.add_argument("--task", default=None,
                    help="override defaults.task (e.g. harness/private_tasks.py for the private split)")
    ap.add_argument("--log-dir", default=None,
                    help="override the base log dir (relative to repo root), e.g. logs/private")
    ap.add_argument("--solver", default=os.environ.get("SOLVER", ""),
                    help="custom agent solver pkg/name for the agent-under-test track")
    ap.add_argument("--dry-run", action="store_true", help="print commands, don't execute")
    args = ap.parse_args()

    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML missing. Run: uv sync")

    if (ROOT / ".env").exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(ROOT / ".env")
        except ImportError:
            pass

    cfg = yaml.safe_load(Path(args.config).read_text())
    defaults = cfg.get("defaults", {})
    task = args.task or defaults.get("task", "inspect_evals/swe_bench")
    log_root = ROOT / (args.log_dir or defaults.get("log_dir", "logs"))
    flags = list(defaults.get("flags", []))

    if args.limit is not None:
        limit = None if args.limit.lower() in ("none", "null", "0", "") else args.limit
    else:
        raw = defaults.get("limit")
        limit = None if (raw in (None, "none", "null", 0)) else raw

    only = {s.strip() for s in args.only.split(",")} if args.only else None

    selected = []
    for m in cfg.get("models", []):
        if only is not None:
            if m["name"] in only:
                selected.append(m)
        elif m.get("enabled", True):
            selected.append(m)

    if not selected:
        sys.exit("No models selected (check 'enabled' flags or --only).")

    rc_total = 0
    for m in selected:
        name, model = m["name"], m["model"]
        env = dict(os.environ)
        for k, v in (m.get("env") or {}).items():
            env[k] = expand(v, os.environ)
        log_dir = log_root / name
        cmd = ["inspect", "eval", task, "--model", model, "--log-dir", str(log_dir)]
        if limit is not None:
            cmd += ["--limit", str(limit)]
        if args.solver:
            cmd += ["--solver", args.solver]
        cmd += flags + list(m.get("solver_args", []))

        print(f"\n=== {name}  ({model}) ===")
        print("  " + " ".join(shlex.quote(c) for c in cmd))
        empty = [k for k, v in (m.get("env") or {}).items() if not expand(v, os.environ)]
        if empty:
            print(f"  ! empty env vars (auth will likely fail): {', '.join(empty)}")
        if "REPLACE" in str(model):
            print("  ! model string is still a placeholder — edit models.yaml")
        if args.dry_run:
            continue
        log_dir.mkdir(parents=True, exist_ok=True)
        rc = subprocess.run(cmd, env=env).returncode
        rc_total |= rc
        if rc != 0:
            print(f"  ! {name} exited with code {rc}")

    sys.exit(rc_total)


if __name__ == "__main__":
    main()
