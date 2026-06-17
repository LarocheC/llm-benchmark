"""Gold reference for mel-filterbank-003 (NEVER shown to the model being benchmarked).

Pure-numpy reproduction of, bit-for-bit:
    librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=n_mels, fmin=fmin, fmax=fmax)
with librosa defaults htk=False (Slaney mel scale) and norm='slaney'.
"""
import numpy as np


def _hz_to_mel(frequencies):
    frequencies = np.asanyarray(frequencies, dtype=np.float64)
    f_min = 0.0
    f_sp = 200.0 / 3
    mels = (frequencies - f_min) / f_sp
    min_log_hz = 1000.0
    min_log_mel = (min_log_hz - f_min) / f_sp
    logstep = np.log(6.4) / 27.0
    if frequencies.ndim:
        log_t = frequencies >= min_log_hz
        mels[log_t] = min_log_mel + np.log(frequencies[log_t] / min_log_hz) / logstep
    elif frequencies >= min_log_hz:
        mels = min_log_mel + np.log(frequencies / min_log_hz) / logstep
    return mels


def _mel_to_hz(mels):
    mels = np.asanyarray(mels, dtype=np.float64)
    f_min = 0.0
    f_sp = 200.0 / 3
    freqs = f_min + f_sp * mels
    min_log_hz = 1000.0
    min_log_mel = (min_log_hz - f_min) / f_sp
    logstep = np.log(6.4) / 27.0
    if mels.ndim:
        log_t = mels >= min_log_mel
        freqs[log_t] = min_log_hz * np.exp(logstep * (mels[log_t] - min_log_mel))
    elif mels >= min_log_mel:
        freqs = min_log_hz * np.exp(logstep * (mels - min_log_mel))
    return freqs


def mel_filterbank(sr, n_fft, n_mels, fmin, fmax):
    n_mels = int(n_mels)
    weights = np.zeros((n_mels, int(1 + n_fft // 2)), dtype=np.float64)

    # Center freqs of each FFT bin (matches librosa.fft_frequencies / np.fft.rfftfreq)
    fftfreqs = np.fft.rfftfreq(n=int(n_fft), d=1.0 / float(sr))

    # n_mels+2 mel band edge freqs, uniformly spaced on the mel axis
    min_mel = _hz_to_mel(float(fmin))
    max_mel = _hz_to_mel(float(fmax))
    mels = np.linspace(min_mel, max_mel, n_mels + 2)
    mel_f = _mel_to_hz(mels)

    fdiff = np.diff(mel_f)
    ramps = np.subtract.outer(mel_f, fftfreqs)

    for i in range(n_mels):
        lower = -ramps[i] / fdiff[i]
        upper = ramps[i + 2] / fdiff[i + 1]
        weights[i] = np.maximum(0, np.minimum(lower, upper))

    # Slaney normalization: approx constant energy per channel
    enorm = 2.0 / (mel_f[2:n_mels + 2] - mel_f[:n_mels])
    weights *= enorm[:, np.newaxis]

    return weights


def make_cases(seed, n):
    """Return n deterministic (sr, n_fft, n_mels, fmin, fmax) tuples.

    Varies sr, n_fft, n_mels, fmin, and exercises both fmax == sr/2 and fmax < sr/2,
    so correctness depends on the mel scale, the three-edge triangle, mel-spaced edges,
    AND the Slaney normalization.
    """
    rng = np.random.default_rng(seed)
    srs = [8000, 16000, 22050]
    n_ffts = [256, 512]
    cases = []
    for _ in range(n):
        sr = int(srs[rng.integers(0, len(srs))])
        n_fft = int(n_ffts[rng.integers(0, len(n_ffts))])
        n_mels = int(rng.integers(8, 41))
        fmin = float(rng.uniform(0.0, 80.0))
        if rng.random() < 0.5:
            fmax = float(sr) / 2.0
        else:
            fmax = float(rng.uniform(0.55, 0.95)) * (float(sr) / 2.0)
        cases.append((sr, n_fft, n_mels, fmin, fmax))
    return cases
