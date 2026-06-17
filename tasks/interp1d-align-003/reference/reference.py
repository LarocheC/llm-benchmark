"""Gold reference for interp1d-align-003 (NEVER shown to the model being benchmarked).

Reproduces torch.nn.functional.interpolate(x, size=size, mode='linear',
align_corners=align_corners) in pure numpy, bit-for-bit in float64.
"""
import numpy as np


def interp1d(x, size, align_corners):
    x = np.asarray(x, dtype=np.float64)
    L_in = x.shape[-1]
    L_out = int(size)
    out = np.empty(x.shape[:-1] + (L_out,), dtype=np.float64)
    for i in range(L_out):
        if align_corners:
            if L_out == 1:
                src = 0.0
            else:
                src = i * (L_in - 1) / (L_out - 1)
        else:
            src = (i + 0.5) * (L_in / L_out) - 0.5
            if src < 0:
                src = 0.0
        i0 = int(np.floor(src))
        if i0 < 0:
            i0 = 0
        if i0 > L_in - 1:
            i0 = L_in - 1
        lam = src - np.floor(src)
        i1 = min(i0 + 1, L_in - 1)
        out[..., i] = (1.0 - lam) * x[..., i0] + lam * x[..., i1]
    return out


def make_cases(seed, n):
    """Return n deterministic (x, size, align_corners) tuples.

    Covers upsample (L_out > L_in) and downsample (L_out < L_in), and both
    align_corners True and False, with varied batch/channel/length shapes.
    """
    rng = np.random.default_rng(seed)
    cases = []
    for k in range(n):
        Nb = int(rng.integers(1, 3))
        C = int(rng.integers(1, 4))
        L_in = int(rng.integers(4, 13))
        L_out = int(rng.integers(3, 21))
        align = bool(k % 2 == 0) if k < 2 else bool(rng.integers(0, 2))
        x = rng.standard_normal(size=(Nb, C, L_in)).astype(np.float64)
        cases.append((x, L_out, align))
    return cases
