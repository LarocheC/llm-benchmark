"""Gold reference for conv1d-torch-003 (NEVER shown to the model being benchmarked).

Pure-numpy reproduction of torch.nn.functional.conv1d with float64 tensors.
"""
import numpy as np


def conv1d(x, weight, bias, stride, padding, dilation, groups):
    x = np.asarray(x, dtype=np.float64)
    weight = np.asarray(weight, dtype=np.float64)
    Nb, C_in, L = x.shape
    C_out, C_in_g, K = weight.shape
    C_out_g = C_out // groups
    assert C_in_g == C_in // groups

    # zero-pad both ends of the length axis
    xpad = np.zeros((Nb, C_in, L + 2 * padding), dtype=np.float64)
    if padding > 0:
        xpad[:, :, padding:padding + L] = x
    else:
        xpad[:, :, :] = x
    Lp = L + 2 * padding

    L_out = (L + 2 * padding - dilation * (K - 1) - 1) // stride + 1
    y = np.zeros((Nb, C_out, L_out), dtype=np.float64)

    for oc in range(C_out):
        g = oc // C_out_g
        in_base = g * C_in_g
        for i in range(L_out):
            start = i * stride
            acc = 0.0
            for c in range(C_in_g):
                for k in range(K):
                    acc += xpad[:, in_base + c, start + k * dilation] * weight[oc, c, k]
            y[:, oc, i] = acc

    if bias is not None:
        bias = np.asarray(bias, dtype=np.float64)
        y += bias.reshape(1, C_out, 1)
    return y


def make_cases(seed, n):
    """Return n deterministic (x, weight, bias, stride, padding, dilation, groups) tuples.

    Inputs vary so that cross-correlation, groups>1, dilation>1, padding>0, stride>1,
    and bias/None all get exercised.
    """
    rng = np.random.default_rng(seed)
    cases = []
    for idx in range(n):
        Nb = int(rng.integers(1, 3))           # 1..2
        groups = int(rng.integers(1, 4))       # 1..3
        C_in_g = int(rng.integers(1, 4))       # 1..3
        C_out_g = int(rng.integers(1, 4))      # 1..3
        C_in = groups * C_in_g
        C_out = groups * C_out_g
        K = int(rng.integers(2, 5))            # 2..4
        L = int(rng.integers(6, 17))           # 6..16
        stride = int(rng.integers(1, 3))       # 1..2
        padding = int(rng.integers(0, 3))      # 0..2
        dilation = int(rng.integers(1, 3))     # 1..2

        # ensure a valid (positive) output length; if not, shrink kernel reach
        eff = dilation * (K - 1) + 1
        while L + 2 * padding < eff:
            L += 1

        x = rng.standard_normal((Nb, C_in, L))
        weight = rng.standard_normal((C_out, C_in_g, K))
        use_bias = bool(rng.integers(0, 2))
        bias = rng.standard_normal((C_out,)) if use_bias else None
        cases.append((x, weight, bias, stride, padding, dilation, groups))
    return cases
