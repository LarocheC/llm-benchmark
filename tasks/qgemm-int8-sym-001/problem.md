# Implement a symmetric per-tensor int8 GEMM with requantization

Write a function:

```python
def qgemm(A, B, scale_a, scale_b, scale_y):
    ...
```

that computes a quantized matrix multiply matching the following EXACT convention.

**Inputs**
- `A`: numpy `int8` array, shape `(M, K)`
- `B`: numpy `int8` array, shape `(K, N)`
- `scale_a`, `scale_b`, `scale_y`: positive Python floats (per-tensor, symmetric quantization, zero-point 0)

**Computation (must match bit-for-bit)**
1. Accumulate the matrix product in **int32** (exact integer arithmetic — NOT float):
   `acc[m, n] = sum_k int32(A[m, k]) * int32(B[k, n])`
2. Requantize to the output scale, in float64:
   `real = acc.astype(float64) * (scale_a * scale_b / scale_y)`
3. Round to the nearest integer, **ties-to-even** (i.e. `numpy.rint` / round-half-to-even).
4. **Saturate** to the int8 range `[-128, 127]`.
5. Return a numpy `int8` array of shape `(M, N)`.

**Notes**
- Do the accumulation in int32 (or wider) integers, NOT in float — float accumulation loses the exact integer sum for large K.
- Round to nearest (ties-to-even); do **not** truncate.
- Saturate (clip) **before** casting to int8 — do not let values wrap around.

Return only the `qgemm` function in a single ```python``` code block.
