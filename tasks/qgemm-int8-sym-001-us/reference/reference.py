"""Gold reference for qgemm-int8-sym-001 (NEVER shown to the model being benchmarked)."""
import numpy as np


def qgemm(A, B, scale_a, scale_b, scale_y):
    A = np.asarray(A, dtype=np.int32)
    B = np.asarray(B, dtype=np.int32)
    acc = A @ B                                    # exact int32 accumulation
    real = acc.astype(np.float64) * (float(scale_a) * float(scale_b) / float(scale_y))
    q = np.rint(real)                              # round half to even
    q = np.clip(q, -128, 127)
    return q.astype(np.int8)


def make_cases(seed, n):
    """Return n deterministic (A, B, scale_a, scale_b, scale_y) tuples.

    Scales are chosen so the requantized values span a mix of in-range and saturated
    outputs, so correctness depends on accumulation width, rounding, AND saturation.
    """
    rng = np.random.default_rng(seed)
    cases = []
    for _ in range(n):
        M = int(rng.integers(1, 6))
        K = int(rng.integers(1, 9))
        N = int(rng.integers(1, 6))
        A = rng.integers(-128, 128, size=(M, K)).astype(np.int8)
        B = rng.integers(-128, 128, size=(K, N)).astype(np.int8)
        sa = float(rng.uniform(0.005, 0.02))
        sb = float(rng.uniform(0.005, 0.02))
        sy = float(rng.uniform(0.02, 0.10))
        cases.append((A, B, sa, sb, sy))
    return cases
