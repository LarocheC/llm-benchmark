# Implement an ONNX QLinearMatMul-style int8 matmul (asymmetric, per-output-channel)

Write a function:

```python
def qlinear_matmul(A, a_scale, a_zp, B, b_scale, b_zp, y_scale, y_zp):
    ...
```

that computes a quantized matrix multiply matching the following EXACT convention. The
activations `A` use **asymmetric** quantization (a single per-tensor zero-point), and the
weights `B` use **per-output-channel** (per-column) scales and zero-points.

**Inputs**
- `A`: numpy `uint8` array, shape `(M, K)` — quantized activations.
- `a_scale`: positive Python `float` (scalar) — activation scale.
- `a_zp`: Python `int` in `[0, 255]` — activation zero-point.
- `B`: numpy `int8` array, shape `(K, N)` — quantized weights.
- `b_scale`: numpy `float64` array, shape `(N,)` — **per-output-channel** scale (one value per
  output column `n`).
- `b_zp`: numpy `int8` array, shape `(N,)` — **per-output-channel** zero-point of `B` (one value
  per output column `n`); may be zero for some/all channels.
- `y_scale`: positive Python `float` (scalar) — output scale.
- `y_zp`: Python `int` in `[0, 255]` — output zero-point.

**Computation (must match bit-for-bit)**
1. Accumulate in **exact int32 integer arithmetic** (NOT float). For each output element,
   subtract the activation zero-point from every `A` element and the **per-column** weight
   zero-point from every `B` element, then take the integer dot product:

   `acc[m, n] = sum_k ( int32(A[m, k]) - int32(a_zp) ) * ( int32(B[k, n]) - int32(b_zp[n]) )`

   Note `b_zp[n]` depends on the output channel `n` only (it is the same for all `k`).
2. Requantize to the output scale, in `float64`. The effective scale is **per-output-channel**
   because `b_scale` is per-column:

   `real[m, n] = float64(acc[m, n]) * ( a_scale * float64(b_scale[n]) / y_scale )`
3. Round to the nearest integer, **ties-to-even** (`numpy.rint` / round-half-to-even), and
   **then** add the output zero-point:

   `q[m, n] = numpy.rint(real[m, n]) + y_zp`
4. **Saturate** `q` to the `uint8` range `[0, 255]` (clip), then return a numpy `uint8` array of
   shape `(M, N)`.

**Notes**
- Do the accumulation in int32 (or wider) integers, NOT in float — float accumulation loses the
  exact integer sum.
- The zero-point subtractions in step 1 are mandatory: `a_zp` is subtracted from every `A`
  element, and the per-channel `b_zp[n]` is subtracted from every `B` element of column `n`.
- `b_scale` is per-output-channel: use `b_scale[n]` for column `n`, NOT a scalar / mean.
- Round to nearest (ties-to-even) with `numpy.rint`; do **not** truncate or floor. Add `y_zp`
  AFTER rounding.
- Saturate (clip) to `[0, 255]` **before** casting to `uint8` — do not let values wrap around,
  and do not clip to the int8 range `[-128, 127]`.

Return only the `qlinear_matmul` function in a single ```python``` code block.
