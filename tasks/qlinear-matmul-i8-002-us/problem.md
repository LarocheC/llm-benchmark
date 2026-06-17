# Implement ONNX Runtime QLinearMatMul (int8 weights, per-output-channel)

Write a function:

```python
def qlinear_matmul(A, a_scale, a_zp, B, b_scale, b_zp, y_scale, y_zp):
    ...
```

that reproduces, bit-for-bit, the ONNX Runtime **QLinearMatMul** operator for the case of
**asymmetric uint8 activations** and **per-output-channel (per-column) int8 weight
quantization**, with a **uint8** quantized output. Match that standard exactly.

**Inputs**
- `A`: numpy `uint8` array, shape `(M, K)` — quantized activations.
- `a_scale`: positive Python `float` (scalar); `a_zp`: Python `int` in `[0, 255]`.
- `B`: numpy `int8` array, shape `(K, N)` — quantized weights, laid out so that column `n` is
  output channel `n` (i.e. `B[k, n]`; the matmul is `A @ B`).
- `b_scale`: numpy `float64` array, shape `(N,)` — one scale per output channel `n`.
- `b_zp`: numpy `int8` array, shape `(N,)` — one zero-point per output channel `n` (may be 0).
- `y_scale`: positive Python `float` (scalar); `y_zp`: Python `int` in `[0, 255]`.

**Output**
- numpy `uint8` array, shape `(M, N)`.

**Conventions (only the arbitrary choices; the method itself is the QLinearMatMul standard)**
- The integer accumulation is exact (use int32 or wider, not floating point).
- Requantization is computed in `float64`.
- No epsilon is added anywhere.

Return only the `qlinear_matmul` function in a single fenced python code block (triple-backtick
python). Use only numpy (do not import torch/scipy/onnxruntime).
