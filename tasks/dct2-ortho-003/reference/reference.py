"""Gold reference for dct2-ortho-003 (NEVER shown to the model being benchmarked).

Reproduces scipy.fft.dct(x, type=2, axis=-1, norm='ortho') in pure numpy.
"""
import numpy as np


def dct2_ortho(x):
    x = np.asarray(x, dtype=np.float64)
    M, N = x.shape
    n = np.arange(N, dtype=np.float64)
    k = np.arange(N, dtype=np.float64)
    # unnormalized DCT-II: y[k] = 2 * sum_n x[n] * cos(pi*(2n+1)*k/(2N))
    cos = np.cos(np.pi * (2.0 * n[None, :] + 1.0) * k[:, None] / (2.0 * N))  # (N, N)
    y = 2.0 * (x @ cos.T)  # (M, N)
    # orthonormal normalization
    scale = np.full(N, np.sqrt(1.0 / (2.0 * N)), dtype=np.float64)
    scale[0] = np.sqrt(1.0 / (4.0 * N))
    return y * scale[None, :]


def make_cases(seed, n):
    """Return n deterministic (x,) tuples; x float64 shape (M, N).

    M in 1..4, N in 4..16, x = standard normal. Varies M and N so the k=0 special
    factor, the k>=1 factor, the cosine convention, and per-row independence are all
    exercised.
    """
    rng = np.random.default_rng(seed)
    cases = []
    for _ in range(n):
        M = int(rng.integers(1, 5))
        N = int(rng.integers(4, 17))
        x = rng.standard_normal((M, N)).astype(np.float64)
        cases.append((x,))
    return cases
