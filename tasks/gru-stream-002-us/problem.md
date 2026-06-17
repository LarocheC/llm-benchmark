# Streaming GRU (PyTorch `torch.nn.GRU` convention) with hidden-state carry

Write a function:

```python
def gru_stream(chunks, h0, w_ih, w_hh, b_ih, b_hh):
    ...
```

Implement a single-layer GRU that exactly reproduces **PyTorch's `torch.nn.GRU`**
(one layer, unidirectional, `batch_first` irrelevant — single sequence) applied to one
input sequence. The sequence does not arrive all at once: it is delivered as consecutive
chunks, and you must process them in a **streaming** fashion, carrying the hidden state
across chunk boundaries so the per-timestep outputs are identical to running the whole
concatenated sequence at once.

## Inputs

Let `H = hidden_size` and `input_size` be the feature dimension.

- `chunks`: a Python `list` of numpy `float64` arrays. Chunk `j` has shape
  `(T_j, input_size)`; concatenating them in order (axis 0) is the full sequence. At
  least one chunk; each `T_j >= 1`.
- `h0`: numpy `float64`, shape `(H,)`. Initial hidden state.
- `w_ih`: numpy `float64`, shape `(3*H, input_size)` — the `weight_ih_l0` tensor.
- `w_hh`: numpy `float64`, shape `(3*H, H)` — the `weight_hh_l0` tensor.
- `b_ih`: numpy `float64`, shape `(3*H,)` — the `bias_ih_l0` tensor.
- `b_hh`: numpy `float64`, shape `(3*H,)` — the `bias_hh_l0` tensor.

The `3*H` rows (and bias slices) follow PyTorch's standard GRU gate layout: the reset
gate occupies rows `0:H`, the update gate rows `H:2H`, and the new/candidate gate rows
`2H:3H`.

## Output

Return `numpy.stack(outputs, axis=0)`: a numpy `float64` array of shape `(total_T, H)`
where `total_T = sum_j T_j`, and row `t` is the hidden state after the `t`-th timestep
of the concatenated sequence.

## Constraints

- Compute in `float64` throughout. The grader compares with `atol=1e-9`, `rtol=1e-7`,
  so follow the exact `torch.nn.GRU` formulation (including how the reset gate enters
  the candidate term and PyTorch's two-separate-bias convention).
- The hidden state must be carried across chunk boundaries, never reset per chunk.

Return only the `gru_stream` function in a single fenced python code block (triple-backtick python).
Use only numpy (do not import torch/scipy/onnxruntime).
