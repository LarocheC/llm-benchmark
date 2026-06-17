# Implement a streaming GRU (PyTorch nn.GRU convention) with hidden-state carry

Write a function:

```python
def gru_stream(chunks, h0, w_ih, w_hh, b_ih, b_hh):
    ...
```

A single GRU layer processes an input sequence that arrives split into consecutive
chunks. You must process it chunk-by-chunk while **carrying the hidden state** across
chunk boundaries, so that the per-timestep outputs are identical to processing the
whole concatenated sequence at once.

## Inputs

Let `H = hidden_size` and `input_size` be the feature dimension.

- `chunks`: a Python `list` of numpy `float64` arrays. Chunk `j` has shape
  `(T_j, input_size)`. Concatenating the chunks in order (along axis 0) forms the full
  input sequence. There is at least one chunk; the `T_j` may differ and each `T_j >= 1`.
- `h0`: numpy `float64`, shape `(H,)`. The initial hidden state.
- `w_ih`: numpy `float64`, shape `(3*H, input_size)`. Input-to-hidden weights.
- `w_hh`: numpy `float64`, shape `(3*H, H)`. Hidden-to-hidden weights.
- `b_ih`: numpy `float64`, shape `(3*H,)`. Input-to-hidden bias.
- `b_hh`: numpy `float64`, shape `(3*H,)`. Hidden-to-hidden bias.

**Gate-row order** (rows of every `3*H` array, and the corresponding bias slices) is
`[r, z, n]`:
- rows `0:H`   -> reset gate `r`
- rows `H:2H`  -> update gate `z`
- rows `2H:3H` -> new/candidate gate `n`

## Computation (must match PyTorch nn.GRU exactly)

Let `sigmoid(u) = 1 / (1 + exp(-u))` and `tanh` be the usual hyperbolic tangent.

Initialise `h = h0`. Maintain a list `outputs = []`. Process every timestep of every
chunk **in order**, **without resetting `h` between chunks** (the state carries over):

For each chunk in `chunks`, for each row `x` (shape `(input_size,)`) of that chunk:

1. `gi = w_ih @ x + b_ih`            (shape `(3H,)`)
2. `gh = w_hh @ h + b_hh`            (shape `(3H,)`)
3. `r = sigmoid( gi[0:H]   + gh[0:H] )`
4. `z = sigmoid( gi[H:2H]  + gh[H:2H] )`
5. `n = tanh( gi[2H:3H] + r * gh[2H:3H] )`
   — note the reset gate `r` multiplies the **hidden** linear-plus-bias term
   `gh[2H:3H]` (i.e. `w_hh[2H:3H] @ h + b_hh[2H:3H]`), **after** that term has been
   fully computed. The reset is applied to the hidden contribution, NOT to `h` before
   the matrix multiply.
6. `h = (1 - z) * n + z * h`
   — the update gate `z` weights the **old** hidden state; `(1 - z)` weights the new
   candidate `n`.
7. Append a copy of `h` to `outputs`.

## Output

Return `numpy.stack(outputs, axis=0)`: a numpy `float64` array of shape
`(total_T, H)` where `total_T = sum_j T_j`. Row `t` is the hidden state after
processing the `t`-th timestep of the concatenated sequence.

## Notes / common mistakes to avoid

- The two biases `b_ih` and `b_hh` are kept **separate** and added inside their
  respective `gi` / `gh` terms; do not collapse them into one combined bias.
- The reset gate multiplies the post-bias hidden term `gh[2H:3H]`, NOT `h` before the
  `w_hh` multiply.
- The blend is `(1 - z) * n + z * h` (z weights the old state), not the reverse.
- Do not reset `h` to `h0` at the start of each chunk — the hidden state is carried.

Return only the `gru_stream` function in a single ```python``` code block.
