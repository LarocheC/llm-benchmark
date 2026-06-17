# Private task split

Hand-authored, **never-published** coding tasks — the contamination-resistant ranking
signal for this benchmark. (Public benchmarks like SWE-bench only *calibrate* the harness;
these are the numbers we trust to actually rank models.)

Each task is one self-contained directory implementing a fixed contract, so any runner can
execute it ("set up the repo, let the agent edit it, run the hidden tests"). The Inspect
runner lives in `../harness/private_tasks.py` (a custom `@task` + scorer that reuses Inspect's
`react()` agent, tools, and sandbox — added alongside the first task).

## Task contract

```
<task-id>/
  meta.yaml         # id, domain, tier, fail_to_pass, pass_to_pass, test_cmd, solution_files
  problem.md        # the issue text shown to the agent (NL description of the bug/feature)
  Dockerfile        # builds the sandbox: installs deps, COPYs repo/ -> /workspace
  repo/             # the BUGGY repo the agent sees and edits (incl. existing PASS_TO_PASS tests)
  hidden_tests/     # FAIL_TO_PASS tests — injected into the sandbox ONLY at scoring time
  solution/         # gold fix (mirrors repo/ paths) — NEVER in the agent's container;
                    #   used only by the well-formedness gate
```

## Scoring (all-or-nothing, SWE-bench style)
A run is **RESOLVED (1.0)** iff, after the agent finishes editing `repo/`:
- every `fail_to_pass` test passes (the bug is actually fixed), **and**
- every `pass_to_pass` test still passes (no regression).

## Well-formedness gate (every task must satisfy before we trust it)
- **gold passes:** apply `solution/` over `repo/` → all `fail_to_pass` AND `pass_to_pass` pass.
- **buggy fails:** with `repo/` as-is → at least one `fail_to_pass` FAILS (the task really tests the
  bug) while all `pass_to_pass` pass.

## Authoring principles
- Original code; never published anywhere (no GitHub / LeetCode / etc.).
- The bug should require **locate → understand → fix → verify**, not a guessable one-liner.
- Hidden tests encode the *desired behavior*; the agent must infer the fix from `problem.md`,
  not by reading the hidden test.
- Deterministic tests (no time / network / randomness) so scoring is stable.
- Calibrate difficulty so current frontier models land ~40–60% on the top tier (resists saturation).
