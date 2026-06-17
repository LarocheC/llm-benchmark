"""Single-shot (non-agentic) runner for code-generation tasks.

The model emits ONE ```python``` block; the scorer runs it against a hidden reference over N
seeded random cases in a Docker sandbox, scoring the FRACTION of cases that match (bit-exact or
within tolerance). Reuses Inspect's generate() solver + a custom fractional scorer.

A codegen task lives under ../tasks/<id>/ with meta.yaml `mode: codegen`:
  meta.yaml   : id, mode: codegen, entry_point, problem_statement, n_cases, seed,
                comparison (exact|allclose [+ atol/rtol])
  problem.md  : the spec shown to the model
  reference/reference.py : gold module providing `<entry_point>(...)` AND `make_cases(seed, n)`
                (a list of arg-tuples). NEVER shown to the model.
  Dockerfile/compose.yaml : sandbox with the deps the reference needs (e.g. numpy).

Run:  inspect eval harness/single_shot.py --model <provider/model>
"""
import json
import re
from pathlib import Path

import yaml

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState, generate, system_message
from inspect_ai.util import SandboxEnvironmentSpec, sandbox

TASKS_ROOT = Path(__file__).resolve().parent.parent / "tasks"
EXEC_TIMEOUT = 60

SYSTEM_PROMPT = (
    "You are an expert Python and numerical-computing engineer. Read the problem and output "
    "EXACTLY ONE ```python``` code block containing the requested function(s) plus any imports "
    "they need, and NOTHING else — no prose, no tests, no example usage."
)

_HARNESS_TMPL = '''
import json, importlib.util
import numpy as np

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

ref = _load("/work/reference.py", "reference")
cases = ref.make_cases(__SEED__, __NCASES__)

def ok(got, want):
    g = np.asarray(got); w = np.asarray(want)
    if g.shape != w.shape:
        return False
    if "__CMP__" == "allclose":
        return bool(np.allclose(g, w, atol=__ATOL__, rtol=__RTOL__))
    return bool(np.array_equal(g, w))

passed = 0; n = len(cases); details = []
try:
    cand = _load("/work/candidate.py", "candidate")
    fn = getattr(cand, "__ENTRY__")
except Exception as e:
    print(json.dumps({"passed": 0, "n": n, "error": "load: " + repr(e)})); raise SystemExit

rfn = getattr(ref, "__ENTRY__")
for i, args in enumerate(cases):
    try:
        if ok(fn(*args), rfn(*args)):
            passed += 1
        elif len(details) < 5:
            details.append("case %d: mismatch" % i)
    except Exception as e:
        if len(details) < 5:
            details.append("case %d: raised %r" % (i, e))
print(json.dumps({"passed": passed, "n": n, "details": details}))
'''


def _harness_src(md):
    return (
        _HARNESS_TMPL
        .replace("__SEED__", str(md.get("seed", 1234)))
        .replace("__NCASES__", str(md.get("n_cases", 50)))
        .replace("__CMP__", str(md.get("comparison", "exact")))
        .replace("__ATOL__", str(md.get("atol", 0)))
        .replace("__RTOL__", str(md.get("rtol", 0)))
        .replace("__ENTRY__", md["entry_point"])
    )


def extract_code(completion: str) -> str:
    m = re.search(r"```(?:python|py)?[ \t]*\r?\n(.*?)```", completion, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    blocks = re.findall(r"```\r?\n?(.*?)```", completion, re.DOTALL)
    if blocks:
        return blocks[-1].strip()
    return completion.strip()


def _codegen_dataset():
    samples = []
    for d in sorted(p for p in TASKS_ROOT.iterdir() if p.is_dir() and (p / "meta.yaml").exists()):
        meta = yaml.safe_load((d / "meta.yaml").read_text())
        if meta.get("mode") != "codegen":
            continue
        problem = (d / meta.get("problem_statement", "problem.md")).read_text()
        samples.append(
            Sample(
                id=meta["id"],
                input=problem,
                metadata={
                    "entry_point": meta["entry_point"],
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


@scorer(metrics=[mean(), stderr()])
def codegen_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        md = state.metadata
        code = extract_code(state.output.completion)
        if not code:
            return Score(value=0.0, explanation="No code block found in completion.")
        await sandbox().write_file("/work/candidate.py", code)
        await sandbox().write_file("/work/reference.py", md["reference_src"])
        await sandbox().write_file("/work/harness.py", _harness_src(md))
        try:
            res = await sandbox().exec(
                ["python", "/work/harness.py"], cwd="/work",
                timeout=EXEC_TIMEOUT, timeout_retry=False,
            )
        except Exception as e:
            return Score(value=0.0, answer=code, explanation=f"exec error: {e!r}")
        last = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""
        try:
            out = json.loads(last)
        except Exception:
            return Score(value=0.0, answer=code,
                         explanation=f"harness produced no JSON.\nstdout:\n{res.stdout}\nstderr:\n{res.stderr}")
        n = out.get("n", 1) or 1
        frac = out.get("passed", 0) / n
        det = (" err: " + out["error"]) if out.get("error") else (" " + " | ".join(out.get("details", [])))
        return Score(value=frac, answer=code,
                     explanation=f"{out.get('passed', 0)}/{n} cases match.{det}")

    return score


@task
def codegen_single_shot():
    return Task(
        dataset=_codegen_dataset(),
        solver=[system_message(SYSTEM_PROMPT), generate()],
        scorer=codegen_scorer(),
    )
