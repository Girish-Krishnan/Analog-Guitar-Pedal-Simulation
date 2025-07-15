import numpy as np
from scipy import signal


def normalize(x):
    """Normalize signal to -1..1"""
    max_val = np.max(np.abs(x))
    if max_val == 0:
        return x
    return x / max_val


def low_pass(x, sr, cutoff=5000):
    b, a = signal.butter(2, cutoff / (sr/2), btype='low')
    return signal.lfilter(b, a, x)
