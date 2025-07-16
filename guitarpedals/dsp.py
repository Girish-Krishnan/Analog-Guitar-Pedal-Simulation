import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def normalize(x):
    """Normalize signal to -1..1"""
    max_val = np.max(np.abs(x))
    if max_val == 0:
        return x
    return x / max_val


def low_pass(x, sr, cutoff=5000):
    b, a = signal.butter(2, cutoff / (sr/2), btype='low')
    return signal.lfilter(b, a, x)


def high_pass(x, sr, cutoff=200):
    """Simple high-pass filter."""
    b, a = signal.butter(2, cutoff / (sr / 2), btype="high")
    return signal.lfilter(b, a, x)


def band_pass(x, sr, low, high):
    """Band-pass filter between ``low`` and ``high``."""
    b, a = signal.butter(2, [low / (sr / 2), high / (sr / 2)], btype="band")
    return signal.lfilter(b, a, x)


def oversample(x, factor=2):
    """Upsample ``x`` by ``factor`` using polyphase filtering."""
    if factor <= 1:
        return x
    return signal.resample_poly(x, factor, 1)


def downsample(x, factor=2):
    """Downsample ``x`` by ``factor`` using polyphase filtering."""
    if factor <= 1:
        return x
    return signal.resample_poly(x, 1, factor)


def convolution_reverb(x, ir):
    """Apply convolution reverb using impulse response ``ir``."""
    y = signal.fftconvolve(x, ir, mode="full")
    return y[: len(x)]


def delay(x, sr, time=0.3, feedback=0.5):
    """Simple feedback delay effect."""
    delay_samples = int(sr * time)
    out = np.zeros(len(x) + delay_samples)
    out[: len(x)] = x
    for i in range(len(x)):
        out[i + delay_samples] += x[i] * feedback
    return out[: len(x)]


def chorus(x, sr, depth_ms=15, rate=0.25):
    """Basic chorus using a modulated delay line."""
    depth = int(sr * depth_ms / 1000)
    t = np.arange(len(x))
    mod = (depth / 2) * (1 + np.sin(2 * np.pi * rate * t / sr))
    out = np.zeros_like(x)
    for i in range(len(x)):
        d = int(mod[i])
        if i - d >= 0:
            out[i] = (x[i] + x[i - d]) / 2
        else:
            out[i] = x[i]
    return out


def save_waveform_plot(x, filename, title=None):
    """Save a simple waveform plot of ``x`` to ``filename``."""
    plt.figure(figsize=(10, 4))
    plt.plot(x)
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
