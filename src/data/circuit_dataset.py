import numpy as np
from torch.utils.data import Dataset

try:
    from PySpice.Spice.Netlist import Circuit
    from PySpice.Unit import u_Ohm, u_F, u_H, u_V, u_A
    from PySpice.Logging.Logging import setup_logging
    import PySpice.Logging.Logging as Logging
    logger = Logging.setup_logging()
except Exception as e:
    print(f"PySpice not available: {e}")
    Circuit = None  # Placeholder if PySpice isn't installed


def simulate_frequency_response(filter_type, params, freqs):
    """Simulate the circuit using PySpice and return magnitude response."""
    if Circuit is None:
        raise RuntimeError("PySpice is required for simulation")

    import math
    circuit = Circuit('Filter')
    source = circuit.SinusoidalVoltageSource('input', 'in', circuit.gnd, amplitude=1@u_V)

    if filter_type == 'lowpass':
        R, C = params['R'], params['C']
        circuit.R(1, 'in', 'out', R @ u_Ohm)
        circuit.C(1, 'out', circuit.gnd, C @ u_F)
    elif filter_type == 'highpass':
        R, C = params['R'], params['C']
        circuit.C(1, 'in', 'out', C @ u_F)
        circuit.R(1, 'out', circuit.gnd, R @ u_Ohm)
    elif filter_type == 'bandpass':
        R, L, C = params['R'], params['L'], params['C']
        circuit.R(1, 'in', 'n1', R @ u_Ohm)
        circuit.L(1, 'n1', 'out', L @ u_H)
        circuit.C(1, 'out', circuit.gnd, C @ u_F)
    else:
        raise ValueError(f"Unknown filter type {filter_type}")

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    # Use a linear sweep so the number of returned points matches ``len(freqs)``
    analysis = simulator.ac(start_frequency=freqs[0], stop_frequency=freqs[-1],
                             number_of_points=len(freqs), variation='lin')
    mag = np.absolute(np.array(analysis.out))
    return mag


class CircuitDataset(Dataset):
    """Dataset generating random filter circuits and their frequency responses."""

    def __init__(self, num_samples=1000, freqs=None):
        if freqs is None:
            freqs = np.logspace(1, 6, num=200)  # 10 Hz to 1 MHz
        self.freqs = freqs
        self.samples = []
        for _ in range(num_samples):
            sample = self._generate_sample()
            self.samples.append(sample)

    def _generate_sample(self):
        filter_type = np.random.choice(['lowpass', 'highpass', 'bandpass'])
        if filter_type == 'lowpass':
            R = np.random.uniform(1e3, 10e3)
            C = np.random.uniform(1e-9, 1e-6)
            params = {'R': R, 'C': C, 'L': 0}
        elif filter_type == 'highpass':
            R = np.random.uniform(1e3, 10e3)
            C = np.random.uniform(1e-9, 1e-6)
            params = {'R': R, 'C': C, 'L': 0}
        else:  # bandpass
            R = np.random.uniform(1e3, 10e3)
            L = np.random.uniform(1e-6, 1e-3)
            C = np.random.uniform(1e-9, 1e-6)
            params = {'R': R, 'L': L, 'C': C}

        if Circuit is not None:
            response = simulate_frequency_response(filter_type, params, self.freqs)
        else:
            response = np.zeros_like(self.freqs)

        # encode filter type as index
        filter_idx = {'lowpass':0, 'highpass':1, 'bandpass':2}[filter_type]
        return {
            'filter_type': filter_idx,
            'response': response,
            'params': np.array([params['R'], params['L'], params['C']])
        }

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        x = np.concatenate([sample['response'], np.array([sample['filter_type']])])
        y = sample['params']
        return x.astype(np.float32), y.astype(np.float32)
