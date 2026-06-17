# Implement an inverse STFT (windowed overlap-add with COLA normalization)

Write a function:

```python
def istft(Z, hop_length, window):
    ...
```

that reconstructs a real signal from its short-time Fourier transform using
windowed overlap-add (OLA) followed by constant-overlap-add (COLA)
normalization by the squared-window envelope. This is the synthesis convention
used by librosa / Griffin-Lim.

**Inputs**
- `Z`: numpy `complex128` array, shape `(n_fft // 2 + 1, n_frames)`. Column `t`
  (i.e. `Z[:, t]`) is the rfft-format (non-negative-frequency half) spectrum of
  frame `t`.
- `hop_length`: Python `int`, the number of samples between successive frames.
- `window`: numpy `float64` array, shape `(n_fft,)`. The SYNTHESIS window, which
  is identical to the analysis window. Define `n_fft = len(window)`.

**Computation (must match exactly)**

Let `n_fft = len(window)` and `T = Z.shape[1]` (the number of frames).

1. Output length:
   `out_len = (T - 1) * hop_length + n_fft`
2. Allocate two `float64` accumulators of length `out_len`:
   `y = zeros(out_len)` and `wsum = zeros(out_len)`.
3. For each frame `t` in `range(T)`:
   - Inverse-transform the column to a real frame of length `n_fft`:
     `frame = numpy.fft.irfft(Z[:, t], n=n_fft)`  (real, length `n_fft`).
   - Let `s = t * hop_length`.
   - Overlap-add the **synthesis-windowed** frame:
     `y[s : s + n_fft] += window * frame`.
   - Accumulate the squared-window envelope:
     `wsum[s : s + n_fft] += window * window`.
4. Normalize only where the envelope is meaningfully nonzero. Compute the mask
   `mask = wsum > 1e-8` and set `y[mask] = y[mask] / wsum[mask]`. Leave
   `y == 0` wherever `mask` is `False` (do NOT divide there — this avoids
   producing `nan`/`inf` at near-silent edges).
5. Return `y`, a `float64` array of shape `(out_len,)`.

**Notes**
- Apply the synthesis `window` to `frame` BEFORE the overlap-add. Do not add the
  raw `irfft` frame.
- The normalization divides by the sum of **squared** windows, not the sum of
  windows.
- Use exactly `out_len = (T - 1) * hop_length + n_fft`.
- The `1e-8` epsilon mask is required: never divide where `wsum <= 1e-8`.

Return only the `istft` function in a single ```python``` code block.
