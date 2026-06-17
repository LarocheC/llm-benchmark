# Build a Slaney mel filterbank matching librosa

Write a function:

```python
def mel_filterbank(sr, n_fft, n_mels, fmin, fmax):
    ...
```

that returns the mel filterbank matrix EXACTLY matching:

```python
librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=n_mels, fmin=fmin, fmax=fmax)
```

evaluated with librosa's defaults `htk=False` (Slaney mel scale) and `norm='slaney'`.

**Inputs**
- `sr`: sampling rate in Hz (e.g. 8000, 16000, 22050).
- `n_fft`: FFT window size (e.g. 256, 512).
- `n_mels`: number of mel bands (positive int).
- `fmin`: lowest frequency in Hz (>= 0).
- `fmax`: highest frequency in Hz (<= sr/2).

**Output**
- A numpy `float64` array of shape `(n_mels, 1 + n_fft // 2)`: row `m` is the
  frequency response of mel band `m` over the FFT bin frequencies.

**Notes**
- The FFT bin frequencies are those of a real FFT of an `n_fft`-point signal sampled
  at `sr` (the `1 + n_fft // 2` non-negative frequencies from 0 up to `sr/2`).
- Use the Slaney auditory-toolbox mel scale and the Slaney filter normalization
  exactly as librosa does (`htk=False`, `norm='slaney'`); match its hz<->mel
  constants so the result agrees to floating-point tolerance.
- You may use ONLY numpy. You may not import librosa (or scipy / torch).

Return only the `mel_filterbank` function in a single fenced python code block
(triple-backtick python). Use only numpy (do not import torch / scipy / librosa).
