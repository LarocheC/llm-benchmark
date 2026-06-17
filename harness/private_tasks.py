"""Inspect AI runner for the private hand-authored task split.

Each task under ../tasks/<id>/ is a self-contained directory (see ../tasks/README.md):
the buggy repo/ -> Docker sandbox, problem.md -> agent prompt, hidden_tests/ -> FAIL_TO_PASS
(injected only at scoring time), solution/ -> gold (gate only, never shipped to the agent).

This reuses Inspect's react() agent + tools + sandbox + multi-provider model layer — the same
machinery validated on SWE-bench — so the model-under-test comparison is identical to the
reuse loop; only the tasks change.

Run:
  inspect eval harness/private_tasks.py --model <provider/model> [--limit N --max-connections K ...]
"""
import shlex
from pathlib import Path

import yaml

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState
from inspect_ai.tool import bash_session, python, text_editor
from inspect_ai.util import SandboxEnvironmentSpec, sandbox

TASKS_ROOT = Path(__file__).resolve().parent.parent / "tasks"
WORKDIR = "/workspace"           # must match the Dockerfile WORKDIR / repo location
TOOL_TIMEOUT = 300               # bash_session/text_editor require >= 210 in inspect_ai 0.3.240

SYSTEM_PROMPT = (
    "You are an expert software engineer working on a standard Ubuntu machine with bash and a "
    "text editor. You will be given an issue to fix. Modify the code on the file system to resolve "
    "it. The repository is already checked out in the current working directory (/workspace); you "
    "do NOT need to change branches or commit. When you are confident the issue is fixed, use your "
    "submit tool."
)


def _load_tasks():
    samples = []
    for d in sorted(p for p in TASKS_ROOT.iterdir() if p.is_dir() and (p / "meta.yaml").exists()):
        meta = yaml.safe_load((d / "meta.yaml").read_text())
        if meta.get("mode", "agentic") != "agentic":
            continue  # non-agentic tasks (e.g. mode: codegen) are handled by harness/single_shot.py
        problem = (d / meta.get("problem_statement", "problem.md")).read_text()
        # Hidden FAIL_TO_PASS tests -> inject into the sandbox at /workspace/<relpath> at score time.
        hidden = {}
        hidden_dir = d / "hidden_tests"
        if hidden_dir.is_dir():
            for f in sorted(hidden_dir.rglob("*.py")):
                rel = f.relative_to(d).as_posix()          # e.g. hidden_tests/test_power_assoc.py
                hidden[f"{WORKDIR}/{rel}"] = f.read_text()
        # Canonical PASS_TO_PASS test files, read from the pristine repo/. Restored into the sandbox
        # at scoring time so the agent cannot weaken or delete the regression tests to game the score.
        canonical = {}
        for t in meta.get("pass_to_pass", []):
            rel = t.split("::", 1)[0]                       # "tests/x.py::test_y" -> "tests/x.py"
            src = d / "repo" / rel
            if src.exists():
                canonical[f"{WORKDIR}/{rel}"] = src.read_text()
        samples.append(
            Sample(
                id=meta["id"],
                input=problem,
                metadata={
                    "fail_to_pass": meta.get("fail_to_pass", []),
                    "pass_to_pass": meta.get("pass_to_pass", []),
                    "test_cmd": meta.get("test_cmd", "python -m pytest -q"),
                    "hidden_tests": hidden,
                    "canonical_tests": canonical,
                },
                sandbox=SandboxEnvironmentSpec(type="docker", config=str(d / "compose.yaml")),
            )
        )
    return samples


async def _run_pytest(targets, test_cmd):
    """Run pytest on the given node targets in the sandbox; return (all_passed, output)."""
    if not targets:
        return True, "(no targets)"
    cmd = test_cmd + " " + " ".join(shlex.quote(t) for t in targets)
    res = await sandbox().exec(["bash", "-c", cmd], cwd=WORKDIR, timeout=TOOL_TIMEOUT)
    return res.returncode == 0, f"$ {cmd}\n(returncode={res.returncode})\n{res.stdout}\n{res.stderr}"


@scorer(metrics=[accuracy(), stderr()])
def private_task_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        md = state.metadata
        # Restore canonical PASS_TO_PASS test files from the pristine repo (defeat test-file
        # tampering), then inject the hidden FAIL_TO_PASS tests. write_file auto-creates parent dirs.
        for path, contents in md.get("canonical_tests", {}).items():
            await sandbox().write_file(path, contents)
        for path, contents in md["hidden_tests"].items():
            await sandbox().write_file(path, contents)
        # Run FAIL_TO_PASS and PASS_TO_PASS separately; BOTH must fully pass (regression guard).
        f2p_ok, f2p_out = await _run_pytest(md["fail_to_pass"], md["test_cmd"])
        p2p_ok, p2p_out = await _run_pytest(md["pass_to_pass"], md["test_cmd"])
        resolved = f2p_ok and p2p_ok
        return Score(
            value=1.0 if resolved else 0.0,
            explanation=(
                f"RESOLVED={resolved}\n\n"
                f"== FAIL_TO_PASS ({'pass' if f2p_ok else 'FAIL'}) ==\n{f2p_out}\n\n"
                f"== PASS_TO_PASS ({'pass' if p2p_ok else 'FAIL'}) ==\n{p2p_out}"
            ),
        )

    return score


@task
def private_tasks():
    return Task(
        dataset=_load_tasks(),
        solver=react(
            prompt=SYSTEM_PROMPT,
            tools=[
                bash_session(timeout=TOOL_TIMEOUT),
                text_editor(timeout=TOOL_TIMEOUT),
                python(timeout=TOOL_TIMEOUT),
            ],
        ),
        scorer=private_task_scorer(),
        message_limit=40,
    )
