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


def save_waveform_plot(x, filename, title=None):
    """Save a simple waveform plot of ``x`` to ``filename``."""
    plt.figure(figsize=(10, 4))
    plt.plot(x)
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
