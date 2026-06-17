# 1D linear interpolation (resampling along the last axis)

Write a function:

```python
def interp1d(x, size, align_corners):
    ...
```

that resamples a 1D signal along its last axis, matching **exactly** the output of

```python
torch.nn.functional.interpolate(x, size=size, mode='linear', align_corners=align_corners)
```

**Inputs**
- `x`: numpy `float64` array of shape `(Nb, C, L_in)` (batch, channels, input length).
- `size`: Python `int`, the desired output length `L_out`.
- `align_corners`: Python `bool` — selects the corner-alignment convention used by
  `torch.nn.functional.interpolate`.

**Output**
- A numpy `float64` array of shape `(Nb, C, L_out)`.

**Notes**
- The result must match `torch.nn.functional.interpolate(x, size=size, mode='linear',
  align_corners=align_corners)` element-for-element (within a tight floating-point tolerance).
- The mapping from each output index to its source coordinate, and the handling of edges,
  differ between the `align_corners=True` and `align_corners=False` cases. Reproduce torch's
  behavior for both.
- `size` may be larger than `L_in` (upsampling) or smaller (downsampling).

Return only the `interp1d` function in a single fenced python code block (triple-backtick
python). Use only numpy (do not import torch / scipy / librosa).
