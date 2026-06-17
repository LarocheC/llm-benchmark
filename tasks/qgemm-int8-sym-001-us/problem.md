# Symmetric per-tensor int8 quantized GEMM

Implement the standard symmetric (zero-point 0) per-tensor **int8 quantized GEMM with
integer requantization**, exactly as performed by an integer inference kernel such as ONNX
Runtime `QGemm` / `MatMulInteger` followed by a per-tensor requantize.

Write a function with this exact signature:

```python
def qgemm(A, B, scale_a, scale_b, scale_y):
    ...
```

**Arguments**
- `A`: numpy `int8` array, shape `(M, K)`.
- `B`: numpy `int8` array, shape `(K, N)` — already in standard GEMM (non-transposed) row layout, i.e. `C = A @ B`.
- `scale_a`, `scale_b`, `scale_y`: positive Python floats. Per-tensor symmetric quantization scales for `A`, `B`, and the output; all zero-points are 0.

**Output**
- A numpy `int8` array of shape `(M, N)`.

**Conventions you must follow (the rest is the standard method)**
- Requantization arithmetic is carried out in `float64`.
- Rounding is round-half-to-even (`numpy.rint`).
- No epsilon is added anywhere.

Return only the `qgemm` function in a single fenced python code block (triple-backtick python).
Use only numpy (do not import torch/scipy/onnxruntime).
