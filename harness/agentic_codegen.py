"""Agentic runner for the single-shot CODEGEN tasks — the second of the two reported modes.

Same tasks, same hidden seeded cases, same fractional scorer as harness/single_shot.py, but the
model works in a react() agent loop with bash/editor/python tools instead of emitting one block.

To make "agentic" meaningfully different from single-shot (and to mirror how the agentic SWE-bench
split gives the agent VISIBLE tests), the agent is handed a DISJOINT set of public example cases it
can test against via /work/check.py, and iterate. Final scoring uses the task's HIDDEN seed/n_cases
(identical to single_shot) so per-task scores are directly comparable across the two modes; the gap
is the metric.

Anti-cheat: the gold reference is written into the sandbox ONLY to generate the public examples, then
DELETED before the agent runs (it never sees the gold or the hidden cases). The public seed is offset
from the hidden seed, so an agent that hard-codes the public input->output pairs does NOT generalize to
the hidden cases. The candidate runs in the numpy-only sandbox, so it cannot import torch/onnxruntime/etc.

Run:  inspect eval harness/agentic_codegen.py --model <provider/model>
"""
import sys
from pathlib import Path

import yaml

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import Generate, TaskState, solver
from inspect_ai.tool import bash_session, python, text_editor
from inspect_ai.util import SandboxEnvironmentSpec, sandbox

sys.path.insert(0, str(Path(__file__).resolve().parent))
from single_shot import _harness_src  # reuse the EXACT hidden-case harness the single-shot scorer runs

TASKS_ROOT = Path(__file__).resolve().parent.parent / "tasks"
WORKDIR = "/work"
TOOL_TIMEOUT = 300                 # bash_session/text_editor require >= 210 in inspect_ai 0.3.240
EXEC_TIMEOUT = 60
PUBLIC_SEED_OFFSET = 1000003       # public examples use a seed disjoint from the hidden scoring seed
N_PUBLIC = 12

SYSTEM_PROMPT = (
    "You are an expert Python and numerical-computing engineer working in a sandbox with bash, a text "
    "editor, and python. Solve the implementation problem you are given.\n"
    "WORKFLOW:\n"
    "- Write your implementation to /work/solution.py, defining a function with the EXACT name requested "
    "in the problem (plus any imports it needs). Use ONLY numpy.\n"
    "- Run `python /work/check.py` to test your solution against a set of public example cases. It prints "
    "how many pass and the first few mismatches. Iterate until they pass.\n"
    "- A DISJOINT hidden set of cases is used for final scoring, so make your function correct in general, "
    "not just on the visible examples.\n"
    "- When you are confident, submit."
)

_PREAMBLE = (
    "Write your solution to the file /work/solution.py, defining a function named `__ENTRY__`. "
    "Test it with `python /work/check.py` (public example cases; a disjoint hidden set is used for "
    "final scoring). Use only numpy.\n\n"
    "----- PROBLEM -----\n"
)

# Generates the public (args, expected) pairs from the reference, INSIDE the sandbox, then is deleted.
_GEN_PUBLIC_TMPL = '''
import pickle, importlib.util
spec = importlib.util.spec_from_file_location("reference", "/work/reference.py")
ref = importlib.util.module_from_spec(spec); spec.loader.exec_module(ref)
cases = ref.make_cases(__PUBSEED__, __NPUB__)
fn = getattr(ref, "__ENTRY__")
data = [(args, fn(*args)) for args in cases]
with open("/work/public_cases.pkl", "wb") as f:
    pickle.dump(data, f)
print("generated", len(data), "public cases")
'''

# Lives in the sandbox for the agent to run; grades /work/solution.py against the public examples.
_CHECK_TMPL = '''
import pickle, importlib.util
import numpy as np

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def ok(got, want):
    g = np.asarray(got); w = np.asarray(want)
    if g.shape != w.shape:
        return False
    if "__CMP__" == "allclose":
        return bool(np.allclose(g, w, atol=__ATOL__, rtol=__RTOL__))
    return bool(np.array_equal(g, w))

with open("/work/public_cases.pkl", "rb") as f:
    data = pickle.load(f)
try:
    sol = _load("/work/solution.py", "solution")
    fn = getattr(sol, "__ENTRY__")
except Exception as e:
    print("ERROR: could not load /work/solution.py and its `__ENTRY__` function: " + repr(e))
    raise SystemExit(1)

passed = 0; msgs = []
for i, (args, want) in enumerate(data):
    try:
        if ok(fn(*args), want):
            passed += 1
        elif len(msgs) < 5:
            msgs.append("  case %d: output does not match expected" % i)
    except Exception as e:
        if len(msgs) < 5:
            msgs.append("  case %d: raised %r" % (i, e))
print("PUBLIC CASES: %d/%d pass" % (passed, len(data)))
for m in msgs:
    print(m)
'''


def _sub(tmpl, md, *, seed=None, ncases=None):
    return (
        tmpl
        .replace("__PUBSEED__", str(seed if seed is not None else md.get("seed", 1234) + PUBLIC_SEED_OFFSET))
        .replace("__NPUB__", str(ncases if ncases is not None else N_PUBLIC))
        .replace("__CMP__", str(md.get("comparison", "exact")))
        .replace("__ATOL__", str(md.get("atol", 0)))
        .replace("__RTOL__", str(md.get("rtol", 0)))
        .replace("__ENTRY__", md["entry_point"])
    )


def _dataset():
    samples = []
    for d in sorted(p for p in TASKS_ROOT.iterdir() if p.is_dir() and (p / "meta.yaml").exists()):
        meta = yaml.safe_load((d / "meta.yaml").read_text())
        if meta.get("mode") != "codegen":
            continue
        problem = (d / meta.get("problem_statement", "problem.md")).read_text()
        entry = meta["entry_point"]
        samples.append(
            Sample(
                id=meta["id"],
                input=_PREAMBLE.replace("__ENTRY__", entry) + problem,
                metadata={
                    "entry_point": entry,
                    "n_cases": meta.get("n_cases", 50),
                    "seed": meta.get("seed", 1234),
                    "comparison": meta.get("comparison", "exact"),
                    "atol": meta.get("atol", 0),
                    "rtol": meta.get("rtol", 0),
                    "reference_src": (d / "reference" / "reference.py").read_text(),
                },
                sandbox=SandboxEnvironmentSpec(type="docker", config=str(d / "compose.yaml")),
            )
        )
    return samples


@solver
def setup_public_cases():
    """Before the agent runs: generate public example cases from the reference, then DELETE the gold."""
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        md = state.metadata
        pub_seed = md["seed"] + PUBLIC_SEED_OFFSET
        await sandbox().write_file(f"{WORKDIR}/reference.py", md["reference_src"])
        await sandbox().write_file(f"{WORKDIR}/_gen_public.py", _sub(_GEN_PUBLIC_TMPL, md, seed=pub_seed, ncases=N_PUBLIC))
        await sandbox().write_file(f"{WORKDIR}/check.py", _sub(_CHECK_TMPL, md))
        await sandbox().exec(["python", f"{WORKDIR}/_gen_public.py"], cwd=WORKDIR, timeout=EXEC_TIMEOUT)
        # Remove the gold + generator so the agent can never read them; keep public_cases.pkl + check.py.
        await sandbox().exec(["rm", "-f", f"{WORKDIR}/reference.py", f"{WORKDIR}/_gen_public.py"], cwd=WORKDIR)
        return state

    return solve


@scorer(metrics=[mean(), stderr()])
def agentic_codegen_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        md = state.metadata
        try:
            code = await sandbox().read_file(f"{WORKDIR}/solution.py")
        except Exception as e:
            return Score(value=0.0, explanation=f"no /work/solution.py produced: {e!r}")
        if not code or not code.strip():
            return Score(value=0.0, explanation="/work/solution.py is empty")
        # Score on the HIDDEN cases (md seed/n_cases) — identical to single_shot, so modes are comparable.
        await sandbox().write_file(f"{WORKDIR}/candidate.py", code)
        await sandbox().write_file(f"{WORKDIR}/reference.py", md["reference_src"])
        await sandbox().write_file(f"{WORKDIR}/harness.py", _harness_src(md))
        try:
            res = await sandbox().exec(["python", f"{WORKDIR}/harness.py"], cwd=WORKDIR,
                                       timeout=EXEC_TIMEOUT, timeout_retry=False)
        except Exception as e:
            return Score(value=0.0, answer=code, explanation=f"exec error: {e!r}")
        import json
        last = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""
        try:
            out = json.loads(last)
        except Exception:
            return Score(value=0.0, answer=code,
                         explanation=f"harness produced no JSON.\nstdout:\n{res.stdout}\nstderr:\n{res.stderr}")
        n = out.get("n", 1) or 1
        frac = out.get("passed", 0) / n
        det = (" err: " + out["error"]) if out.get("error") else (" " + " | ".join(out.get("details", [])))
        return Score(value=frac, answer=code, explanation=f"{out.get('passed', 0)}/{n} hidden cases match.{det}")

    return score


@task
def agentic_codegen():
    return Task(
        dataset=_dataset(),
        solver=[
            setup_public_cases(),
            react(
                prompt=SYSTEM_PROMPT,
                tools=[
                    bash_session(timeout=TOOL_TIMEOUT),
                    text_editor(timeout=TOOL_TIMEOUT),
                    python(timeout=TOOL_TIMEOUT),
                ],
            ),
        ],
        scorer=agentic_codegen_scorer(),
        message_limit=40,
    )
