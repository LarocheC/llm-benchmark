"""Gold reference for qlinear-matmul-i8-002 (NEVER shown to the model being benchmarked)."""
import numpy as np


def qlinear_matmul(A, a_scale, a_zp, B, b_scale, b_zp, y_scale, y_zp):
    A = np.asarray(A, dtype=np.int32)
    B = np.asarray(B, dtype=np.int32)
    b_zp = np.asarray(b_zp, dtype=np.int32)            # shape (N,)
    b_scale = np.asarray(b_scale, dtype=np.float64)    # shape (N,)

    # step 1: exact int32 accumulation with zero-point subtraction.
    Ac = A - np.int32(a_zp)                             # (M, K)
    Bc = B - b_zp[None, :]                              # (K, N) minus per-column zp
    acc = Ac @ Bc                                       # (M, N), exact integer

    # step 2: per-output-channel requantization in float64.
    eff = float(a_scale) * b_scale / float(y_scale)    # (N,)
    real = acc.astype(np.float64) * eff[None, :]        # (M, N)

    # step 3: round half to even, THEN add output zero-point.
    q = np.rint(real) + np.int32(y_zp)

    # step 4: saturate to uint8 range and cast.
    q = np.clip(q, 0, 255)
    return q.astype(np.uint8)


def make_cases(seed, n):
    """Return n deterministic arg-tuples for qlinear_matmul.

    Scales / zero-points are tuned so outputs span saturated-low (0), mid-range, and
    saturated-high (255), exercising zero-point subtraction, per-channel scaling, the
    +y_zp offset, ties-to-even rounding, and uint8 saturation.
    """
    rng = np.random.default_rng(seed)
    cases = []
    for i in range(n):
        M = int(rng.integers(1, 7))
        K = int(rng.integers(1, 7))
        N = int(rng.integers(1, 7))
        A = rng.integers(0, 256, size=(M, K)).astype(np.uint8)
        a_scale = float(rng.uniform(0.02, 0.2))
        a_zp = int(rng.integers(0, 256))
        B = rng.integers(-128, 128, size=(K, N)).astype(np.int8)
        b_scale = rng.uniform(0.001, 0.02, size=N).astype(np.float64)
        b_zp = rng.integers(-8, 8, size=N).astype(np.int8)
        # occasionally force some/all b_zp to 0 to exercise that branch
        if i % 5 == 0:
            b_zp = np.zeros(N, dtype=np.int8)
        elif i % 5 == 1 and N > 1:
            b_zp[0] = np.int8(0)
        y_scale = float(rng.uniform(0.02, 0.2))
        y_zp = int(rng.integers(0, 256))
        cases.append((A, a_scale, a_zp, B, b_scale, b_zp, y_scale, y_zp))
    return cases
