import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from PySpice.Unit import *
from PySpice.Logging.Logging import setup_logging
import os
from scipy import signal
import librosa

from .generate import generate_riff
from .dsp import normalize, low_pass
from .circuits import fuzz_circuit, overdrive_circuit

setup_logging()


def simulate_circuit(circuit, input_wave, fs, target_fs=8000):
    """Run a transient simulation of ``circuit`` using ``input_wave``.

    The previous implementation ignored ``input_wave`` and drove the circuit
    with a sinusoidal voltage source.  We now feed the actual audio samples by
    creating a piece-wise linear voltage source that follows the waveform.

    To keep the number of points manageable (which speeds up
    ``PieceWiseLinearVoltageSource`` creation), ``input_wave`` can be resampled
    to ``target_fs`` if the original ``fs`` is higher.  Resampling uses
    ``librosa`` when available and falls back to ``scipy.signal`` otherwise.
    """

    orig_len = len(input_wave)
    print("Length of input wave:", orig_len)
    print("Sampling rate:", fs)
    orig_fs = fs
    if target_fs and fs > target_fs:
        input_wave = librosa.resample(np.asarray(input_wave), orig_sr=fs, target_sr=target_fs)
        print("Resampled input wave length:", len(input_wave))
        fs = target_fs

    step = 1 / fs @ u_s

    # Create (time, value) pairs for the voltage source.
    times = np.arange(len(input_wave)) / fs
    values = [(t @ u_s, float(v) @ u_V) for t, v in zip(times, input_wave)]

    print("Creating PieceWiseLinearVoltageSource with", len(values), "points")

    circuit.PieceWiseLinearVoltageSource(
        'input', 'in', circuit.gnd, values=values, dc=float(input_wave[0]) @ u_V
    )

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=step, end_time=len(input_wave) / fs @ u_s)
    out = np.array(analysis.out)
    
    print("Simulation complete, output length:", len(out))

    # Resample back to the original sampling rate if it was changed during
    # simulation.  Ngspice can also return a variable number of samples so we
    # resample again to match the original input length.  ``signal.resample`` is
    # used here because it operates purely on the sample count regardless of the
    # current sampling rate.
    if fs != orig_fs:
        out = librosa.resample(out, orig_sr=fs, target_sr=orig_fs)
        fs = orig_fs

    if len(out) != orig_len:
        out = signal.resample(out, orig_len)

    print("Output length:", len(out))
    print("Output sampling rate:", fs)

    return out


def main():
    os.makedirs('outputs', exist_ok=True)
    audio, fs = generate_riff()
    audio = normalize(audio)
    plt.figure(figsize=(10,4))
    plt.plot(audio)
    plt.title('Input Audio Waveform')
    plt.tight_layout()
    plt.savefig('outputs/input_waveform.png')

    circuit = fuzz_circuit()
    y = simulate_circuit(circuit, audio, fs)
    # y = normalize(low_pass(y, fs))
    y = normalize(y)
    sf.write('outputs/fuzz.wav', y, fs)

    plt.figure(figsize=(10,4))
    plt.plot(y)
    plt.title('Fuzz Output')
    plt.tight_layout()
    plt.savefig('outputs/fuzz_waveform.png')

if __name__ == '__main__':
    main()
