#!/usr/bin/env python3
"""Preflight checks for the SWE-bench reuse loop.

Runnable WITHOUT any provider credentials — it reports exactly what is ready
and what you still need to fill in. Run:  uv run python scripts/preflight.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OK, WARN, BAD = "[ ok ]", "[warn]", "[FAIL]"


def line(status: str, msg: str) -> None:
    print(f"{status} {msg}")


def main() -> None:
    # .env
    if (ROOT / ".env").exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(ROOT / ".env")
            line(OK, ".env found and loaded")
        except Exception:
            line(WARN, ".env found but python-dotenv missing (run: uv sync)")
    else:
        line(WARN, "no .env yet (cp .env.example .env, then fill provider creds)")

    # packages
    try:
        import inspect_ai

        line(OK, f"inspect_ai {getattr(inspect_ai, '__version__', '?')}")
    except Exception as e:
        line(BAD, f"inspect_ai not importable: {e}  -> run: uv sync")
    try:
        import inspect_evals  # noqa: F401

        line(OK, "inspect_evals importable")
    except Exception as e:
        line(BAD, f"inspect_evals not importable: {e}  -> run: uv sync")
    try:
        import importlib

        importlib.import_module("inspect_evals.swe_bench")
        line(OK, "inspect_evals.swe_bench task importable")
    except Exception as e:
        line(WARN, f"could not import swe_bench task: {e}")

    # inspect CLI
    if shutil.which("inspect"):
        line(OK, "`inspect` CLI on PATH")
    else:
        line(WARN, "`inspect` not on PATH (use `uv run inspect ...`)")

    # docker
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=20)
        line(OK if r.returncode == 0 else BAD,
             "docker daemon reachable" if r.returncode == 0
             else "docker installed but daemon not reachable (start Docker)")
    except Exception as e:
        line(BAD, f"docker not usable: {e}")

    # ghcr login (best-effort: needed to pull Epoch AI instance images)
    cfgp = Path.home() / ".docker" / "config.json"
    ghcr = False
    if cfgp.exists():
        try:
            ghcr = any("ghcr.io" in k for k in json.loads(cfgp.read_text()).get("auths", {}))
        except Exception:
            pass
    line(OK if ghcr else WARN,
         "ghcr.io docker login present" if ghcr else
         "no ghcr.io login (gh auth token | docker login ghcr.io -u <user> --password-stdin)")

    # ollama (best-effort)
    try:
        base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1").rstrip("/")
        tags_url = base[:-3] + "/api/tags" if base.endswith("/v1") else base + "/api/tags"
        with urllib.request.urlopen(tags_url, timeout=3) as resp:
            data = json.loads(resp.read())
        names = [m.get("name") for m in data.get("models", [])]
        line(OK, f"ollama reachable; models pulled: {', '.join(n for n in names if n) or '(none)'}")
    except Exception:
        line(WARN, "ollama not reachable (run `ollama serve`, then `ollama pull llama3.1`)")

    # per-model env readiness from models.yaml
    try:
        import yaml

        cfg = yaml.safe_load((ROOT / "models.yaml").read_text())
        print("\nmodels.yaml readiness:")
        for m in cfg.get("models", []):
            name, model = m["name"], str(m["model"])
            tag = "enabled" if m.get("enabled", True) else "disabled"
            missing = [
                k for k, v in (m.get("env") or {}).items()
                if isinstance(v, str) and v.startswith("${") and not os.environ.get(v[2:-1])
            ]
            placeholder = "REPLACE" in model
            notes = []
            if placeholder:
                notes.append("model string is still a placeholder")
            if missing:
                notes.append("unset env: " + ", ".join(missing))
            status = OK if (not placeholder and not missing) else WARN
            line(status, f"{name} [{tag}] {model}" + (f"  ({'; '.join(notes)})" if notes else ""))
    except Exception as e:
        line(WARN, f"could not parse models.yaml: {e}")


if __name__ == "__main__":
    main()
