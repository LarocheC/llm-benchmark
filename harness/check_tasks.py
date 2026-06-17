#!/usr/bin/env python3
"""Well-formedness gate for the private task split (see ../tasks/README.md).

For each task it builds the Docker image and verifies, IN THE REAL SANDBOX ENV:
  (1) buggy repo   -> FAIL_TO_PASS fails  AND  PASS_TO_PASS passes
  (2) gold applied -> FAIL_TO_PASS passes AND  PASS_TO_PASS passes
A task that fails either check is ill-formed (doesn't test the bug, or the gold is wrong, or a
regression). Exits non-zero if any task is ill-formed — wire this into CI before trusting scores.

Usage:  uv run python harness/check_tasks.py [task-id ...]   (default: all tasks)
"""
import base64
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

TASKS_ROOT = Path(__file__).resolve().parent.parent / "tasks"
WORKDIR = "/workspace"


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def _inject_cmds(files, base_dir):
    """Shell commands to write each file (path relative to base_dir) into the container via base64."""
    cmds = []
    for rel, src in files:
        b64 = base64.b64encode(src.read_bytes()).decode()
        q = shlex.quote(rel)
        cmds.append(f"mkdir -p {WORKDIR}/$(dirname {q}) && echo {b64} | base64 -d > {WORKDIR}/{q}")
    return "\n".join(cmds)


def _pytest(image, setup_sh, targets):
    tgt = " ".join(shlex.quote(t) for t in targets)
    script = f"{setup_sh}\npython -m pytest -q {tgt}"
    return _run(["docker", "run", "--rm", "--network", "none", "-w", WORKDIR, image, "bash", "-c", script])


def check_task(d: Path) -> bool:
    meta = yaml.safe_load((d / "meta.yaml").read_text())
    tid = meta["id"]
    f2p, p2p = meta.get("fail_to_pass", []), meta.get("pass_to_pass", [])
    image = f"privtask-{tid}".lower()

    print(f"[{tid}] building image…")
    b = _run(["docker", "build", "-q", "-t", image, str(d)])
    if b.returncode != 0:
        print(f"  ✗ BUILD FAILED:\n{b.stderr[-1000:]}")
        return False

    hidden = [(f.relative_to(d).as_posix(), f) for f in sorted((d / "hidden_tests").rglob("*.py"))] \
        if (d / "hidden_tests").is_dir() else []
    inject = _inject_cmds(hidden, d)
    gold = [(sf, d / "solution" / sf) for sf in meta.get("solution_files", [])]
    apply_gold = inject + "\n" + _inject_cmds(gold, d)

    ok = True
    # (1) buggy
    if _pytest(image, inject, f2p).returncode == 0:
        print("  ✗ buggy FAIL_TO_PASS unexpectedly PASSED (task does not actually test the bug)"); ok = False
    else:
        print("  ✓ buggy FAIL_TO_PASS fails (as expected)")
    r = _pytest(image, inject, p2p)
    if r.returncode != 0:
        print(f"  ✗ buggy PASS_TO_PASS failed:\n{r.stdout[-600:]}"); ok = False
    else:
        print("  ✓ buggy PASS_TO_PASS passes")
    # (2) gold
    r = _pytest(image, apply_gold, f2p + p2p)
    if r.returncode != 0:
        print(f"  ✗ GOLD did not pass all tests:\n{r.stdout[-600:]}"); ok = False
    else:
        print("  ✓ gold passes FAIL_TO_PASS + PASS_TO_PASS")

    print(f"[{tid}] {'WELL-FORMED ✓' if ok else 'ILL-FORMED ✗'}\n")
    return ok


def main():
    wanted = set(sys.argv[1:])
    dirs = [p for p in sorted(TASKS_ROOT.iterdir()) if p.is_dir() and (p / "meta.yaml").exists()]
    if wanted:
        dirs = [p for p in dirs if p.name in wanted]
    if not dirs:
        print("no tasks found"); sys.exit(1)
    results = [check_task(d) for d in dirs]
    print(f"{sum(results)}/{len(results)} tasks well-formed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
