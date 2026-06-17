"""Gold reference for gru-stream-002 (NEVER shown to the model being benchmarked).

Streaming single-layer GRU following PyTorch nn.GRU conventions, carrying hidden
state across chunk boundaries. Gate row order is [r, z, n].
"""
import numpy as np


def _sigmoid(u):
    return 1.0 / (1.0 + np.exp(-u))


def gru_stream(chunks, h0, w_ih, w_hh, b_ih, b_hh):
    h = np.asarray(h0, dtype=np.float64).copy()
    H = h.shape[0]
    w_ih = np.asarray(w_ih, dtype=np.float64)
    w_hh = np.asarray(w_hh, dtype=np.float64)
    b_ih = np.asarray(b_ih, dtype=np.float64)
    b_hh = np.asarray(b_hh, dtype=np.float64)

    outputs = []
    for chunk in chunks:
        chunk = np.asarray(chunk, dtype=np.float64)
        for x in chunk:
            gi = w_ih @ x + b_ih
            gh = w_hh @ h + b_hh
            r = _sigmoid(gi[0:H] + gh[0:H])
            z = _sigmoid(gi[H:2 * H] + gh[H:2 * H])
            n = np.tanh(gi[2 * H:3 * H] + r * gh[2 * H:3 * H])
            h = (1.0 - z) * n + z * h
            outputs.append(h.copy())
    return np.stack(outputs, axis=0)


def make_cases(seed, n):
    """Return n deterministic (chunks, h0, w_ih, w_hh, b_ih, b_hh) tuples.

    Shapes vary: input_size 2..4, hidden_size 2..4, total_T 5..12, split into 1..4
    chunks of varying (>=1) length. Weights/biases/h0 are scaled so gate values span a
    range that exercises sigmoid/tanh nonlinearity, the separate biases, the reset's
    placement on the hidden term, the (1-z)/z blend direction, the [r,z,n] ordering,
    and genuine cross-chunk state carry (multi-chunk cases where the boundary matters).
    """
    rng = np.random.default_rng(seed)
    cases = []
    for _ in range(n):
        input_size = int(rng.integers(2, 5))
        H = int(rng.integers(2, 5))
        total_T = int(rng.integers(5, 13))

        # split total_T into n_chunks parts, each >= 1
        max_chunks = min(4, total_T)
        n_chunks = int(rng.integers(1, max_chunks + 1))
        # random composition of total_T into n_chunks positive parts
        if n_chunks == 1:
            sizes = [total_T]
        else:
            # choose n_chunks-1 distinct cut points in 1..total_T-1
            cuts = np.sort(rng.choice(np.arange(1, total_T), size=n_chunks - 1, replace=False))
            bounds = np.concatenate(([0], cuts, [total_T]))
            sizes = [int(bounds[i + 1] - bounds[i]) for i in range(n_chunks)]

        full = rng.standard_normal((total_T, input_size)) * 1.0
        chunks = []
        off = 0
        for s in sizes:
            chunks.append(full[off:off + s].astype(np.float64).copy())
            off += s

        h0 = (rng.standard_normal(H) * 0.3).astype(np.float64)
        w_ih = (rng.standard_normal((3 * H, input_size)) * 0.5).astype(np.float64)
        w_hh = (rng.standard_normal((3 * H, H)) * 0.5).astype(np.float64)
        b_ih = (rng.standard_normal(3 * H) * 0.3).astype(np.float64)
        b_hh = (rng.standard_normal(3 * H) * 0.3).astype(np.float64)

        cases.append((chunks, h0, w_ih, w_hh, b_ih, b_hh))
    return cases
