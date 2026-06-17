#!/usr/bin/env python3
"""Well-formedness gate for single-shot CODEGEN tasks (meta `mode: codegen`).

For each codegen task it builds the Docker image and runs the EXACT single-shot harness
(harness/single_shot.py) with the GOLD reference supplied as the candidate. This confirms,
IN THE REAL SANDBOX, that:
  - the reference module imports with the image's deps and `make_cases(seed, n)` runs,
  - `<entry_point>` is callable and returns a shape/dtype the comparator accepts,
  - the gold scores a perfect n/n (self-consistent + deterministic),
  - everything completes within the exec timeout.

It does NOT prove the reference encodes the intended math — that's the job of the clean-room
cross-check done during authoring. This is the sandbox/plumbing gate; wire it into CI.

Usage:  uv run python harness/check_codegen.py [task-id ...]   (default: all codegen tasks)
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from single_shot import _harness_src  # the exact harness the scorer runs

TASKS_ROOT = Path(__file__).resolve().parent.parent / "tasks"
WORKDIR = "/work"


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def _b64_write(rel, text):
    b64 = base64.b64encode(text.encode()).decode()
    return f"echo {b64} | base64 -d > {WORKDIR}/{rel}"


def check_task(d: Path) -> bool:
    meta = yaml.safe_load((d / "meta.yaml").read_text())
    tid = meta["id"]
    image = f"codegentask-{tid}".lower()

    print(f"[{tid}] building image…")
    b = _run(["docker", "build", "-q", "-t", image, str(d)])
    if b.returncode != 0:
        print(f"  ✗ BUILD FAILED:\n{b.stderr[-1000:]}")
        return False

    ref_src = (d / "reference" / "reference.py").read_text()
    md = {
        "seed": meta.get("seed", 1234),
        "n_cases": meta.get("n_cases", 50),
        "comparison": meta.get("comparison", "exact"),
        "atol": meta.get("atol", 0),
        "rtol": meta.get("rtol", 0),
        "entry_point": meta["entry_point"],
    }
    # The gold reference IS the candidate -> must score a perfect n/n in the real sandbox.
    setup = "\n".join([
        _b64_write("candidate.py", ref_src),
        _b64_write("reference.py", ref_src),
        _b64_write("harness.py", _harness_src(md)),
    ])
    script = f"{setup}\npython {WORKDIR}/harness.py"
    r = _run(["docker", "run", "--rm", "--network", "none", "-w", WORKDIR, image, "bash", "-c", script])
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    try:
        out = json.loads(last)
    except Exception:
        print(f"  ✗ harness produced no JSON\n  stdout: {r.stdout[-600:]}\n  stderr: {r.stderr[-600:]}")
        return False
    if out.get("error"):
        print(f"  ✗ harness error: {out['error']}")
        return False
    n, passed = out.get("n", 0), out.get("passed", 0)
    if n == 0 or passed != n:
        print(f"  ✗ gold scored {passed}/{n} (expected perfect); details: {out.get('details')}")
        return False
    print(f"  ✓ gold scores {passed}/{n} in the real sandbox")
    print(f"[{tid}] WELL-FORMED ✓\n")
    return True


def main():
    wanted = set(sys.argv[1:])
    dirs = [p for p in sorted(TASKS_ROOT.iterdir()) if p.is_dir() and (p / "meta.yaml").exists()]
    codegen = [p for p in dirs if yaml.safe_load((p / "meta.yaml").read_text()).get("mode") == "codegen"]
    if wanted:
        codegen = [p for p in codegen if p.name in wanted]
    if not codegen:
        print("no codegen tasks found"); sys.exit(1)
    results = [check_task(d) for d in codegen]
    print(f"{sum(results)}/{len(results)} codegen tasks well-formed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
