"""Gold reference for istft-cola-002 (NEVER shown to the model being benchmarked)."""
import numpy as np


def istft(Z, hop_length, window):
    window = np.asarray(window, dtype=np.float64)
    Z = np.asarray(Z, dtype=np.complex128)
    n_fft = len(window)
    T = Z.shape[1]
    out_len = (T - 1) * int(hop_length) + n_fft
    y = np.zeros(out_len, dtype=np.float64)
    wsum = np.zeros(out_len, dtype=np.float64)
    for t in range(T):
        frame = np.fft.irfft(Z[:, t], n=n_fft)        # real, length n_fft
        s = t * int(hop_length)
        y[s : s + n_fft] += window * frame            # synthesis-windowed OLA
        wsum[s : s + n_fft] += window * window        # COLA squared-window envelope
    mask = wsum > 1e-8
    y[mask] = y[mask] / wsum[mask]
    return y


def make_cases(seed, n):
    """Return n deterministic (Z, hop_length, window) tuples.

    n_fft in {16, 32}; T random in 3..8; hop_length = n_fft // 4 (75% overlap);
    window = periodic Hann; Z random complex128 in rfft format. Random Z fully
    exercises irfft + windowed OLA + the squared-window COLA normalization, while
    the 1e-8 mask keeps the near-silent edges identical across correct impls.
    """
    rng = np.random.default_rng(seed)
    cases = []
    for _ in range(n):
        n_fft = int(rng.choice([16, 32]))
        T = int(rng.integers(3, 9))
        hop_length = n_fft // 4
        window = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(n_fft) / n_fft)
        window = window.astype(np.float64)
        n_bins = n_fft // 2 + 1
        Z = (rng.standard_normal((n_bins, T)) + 1j * rng.standard_normal((n_bins, T))).astype(np.complex128)
        cases.append((Z, hop_length, window))
    return cases
