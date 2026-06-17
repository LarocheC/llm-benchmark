# Inverse STFT (weighted overlap-add, COLA synthesis)

Write a function:

```python
def istft(Z, hop_length, window):
    ...
```

that performs the canonical **inverse short-time Fourier transform** via
**weighted overlap-add with constant-overlap-add (COLA) squared-window
normalization** — the synthesis convention used by librosa / Griffin-Lim. You
are expected to know this standard reconstruction.

**Signature / contract (the arbitrary parts, pinned)**
- `Z`: numpy `complex128` array, shape `(n_fft // 2 + 1, n_frames)`. Column
  `Z[:, t]` is the rfft-format (non-negative-frequency half) spectrum of frame
  `t`.
- `hop_length`: Python `int`, samples between successive frames.
- `window`: numpy `float64` array, shape `(n_fft,)`, used as BOTH the analysis
  and synthesis window. Define `n_fft = len(window)`.
- Output: a real `float64` array of shape `(out_len,)` with
  `out_len = (n_frames - 1) * hop_length + n_fft` (no trimming, no centering).
- Recover each time-domain frame with `numpy.fft.irfft(Z[:, t], n=n_fft)`.
- Normalization is by the sum of **squared** synthesis windows. Use an epsilon
  of `1e-8`: leave the output at `0` wherever the squared-window envelope is
  `<= 1e-8` (do not divide there).

Return only the `istft` function in a single fenced python code block
(triple-backtick python). Use only numpy (do not import torch/scipy/onnxruntime).
