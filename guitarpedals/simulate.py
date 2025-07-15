import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from PySpice.Unit import *
from PySpice.Logging.Logging import setup_logging
import os

from .generate import generate_riff
from .dsp import normalize, low_pass
from .circuits import fuzz_circuit, overdrive_circuit

setup_logging()


def simulate_circuit(circuit, input_wave, fs):
    """Run a transient simulation of ``circuit`` using ``input_wave``.

    The previous implementation ignored ``input_wave`` and drove the circuit
    with a sinusoidal voltage source.  We now feed the actual audio samples by
    creating a piece-wise linear voltage source that follows the waveform.
    """

    step = 1 / fs @ u_s

    # Create (time, value) pairs for the voltage source.
    times = np.arange(len(input_wave)) / fs
    values = [(t @ u_s, float(v) @ u_V) for t, v in zip(times, input_wave)]

    circuit.PieceWiseLinearVoltageSource(
        'input', 'in', circuit.gnd, values=values, dc=0 @ u_V
    )

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=step, end_time=len(input_wave) / fs @ u_s)
    out = np.array(analysis.out)
    return out


def main():
    os.makedirs('outputs', exist_ok=True)
    audio, fs = generate_riff()
    audio = normalize(audio)
    plt.figure(figsize=(10,4))
    plt.plot(audio[:1000])
    plt.title('Input Audio Waveform (first 1000 samples)')
    plt.tight_layout()
    plt.savefig('outputs/input_waveform.png')

    circuit = fuzz_circuit()
    y = simulate_circuit(circuit, audio, fs)
    y = normalize(low_pass(y, fs))
    sf.write('outputs/fuzz.wav', y, fs)

    plt.figure(figsize=(10,4))
    plt.plot(y[:1000])
    plt.title('Fuzz Output (first 1000 samples)')
    plt.tight_layout()
    plt.savefig('outputs/fuzz_waveform.png')

if __name__ == '__main__':
    main()
