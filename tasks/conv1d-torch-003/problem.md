# Implement 1-D convolution matching `torch.nn.functional.conv1d`

Write a function:

```python
def conv1d(x, weight, bias, stride, padding, dilation, groups):
    ...
```

whose output is numerically identical to
`torch.nn.functional.conv1d(x, weight, bias, stride=stride, padding=padding, dilation=dilation, groups=groups)`
evaluated with **float64** tensors.

**Inputs**
- `x`: numpy `float64` array, shape `(Nb, C_in, L)` (batch, input channels, length).
- `weight`: numpy `float64` array, shape `(C_out, C_in // groups, K)`.
- `bias`: numpy `float64` array of shape `(C_out,)`, **or `None`**.
- `stride`, `padding`, `dilation`, `groups`: non-negative Python ints (`stride >= 1`, `groups >= 1`, `dilation >= 1`, `padding >= 0`).

**Output**
- numpy `float64` array of shape `(Nb, C_out, L_out)`, where `L_out` is whatever
  `torch.nn.functional.conv1d` produces for the given arguments.

**Notes**
- The semantics (kernel orientation, how `groups` partitions the input/output channels,
  how `dilation`/`padding`/`stride` enter, and the exact `L_out`) are defined by
  `torch.nn.functional.conv1d`. Match it exactly.
- `bias` may be `None` (no bias term added).
- You may use **only numpy** (do not import torch / scipy / librosa).

Return only the `conv1d` function in a single fenced python code block (triple-backtick python). Use only numpy (do not import torch / scipy / librosa).
