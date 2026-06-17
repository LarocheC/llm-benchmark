# Orthonormal DCT-II along the last axis

Write a function:

```python
def dct2_ortho(x):
    ...
```

that returns exactly the same result as

```python
scipy.fft.dct(x, type=2, axis=-1, norm='ortho')
```

**Inputs**
- `x`: numpy `float64` array, shape `(M, N)`.

**Output**
- A numpy `float64` array of shape `(M, N)`: the type-2 DCT with orthonormal
  (`norm='ortho'`) normalization applied **independently to each row** (i.e. along
  the last axis).

**Constraints**
- You may use **only numpy**. Do **not** import `scipy` (or any other library); the
  reference implementation is checked against `scipy.fft.dct` but your code may not
  call it.
- Match the SciPy result to within `atol=1e-9`, `rtol=1e-7`.

Return only the `dct2_ortho` function in a single fenced python code block
(triple-backtick python). Use only numpy (do not import torch / scipy / librosa).
