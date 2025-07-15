import argparse
import torch
import numpy as np
import matplotlib.pyplot as plt

from src.models.vae import VAE
from src.data.circuit_dataset import simulate_frequency_response


FILTER_TYPES = ['lowpass', 'highpass', 'bandpass', 'bandstop']


def load_model(model_path, input_dim, latent_dim):
    model = VAE(input_dim=input_dim, latent_dim=latent_dim)
    checkpoint = torch.load(model_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    freqs = checkpoint['freqs']
    return model, freqs


def design_circuit(model, target_response, filter_type):
    model.eval()
    filter_idx = FILTER_TYPES.index(filter_type)
    inp = np.concatenate([target_response, np.array([filter_idx])]).astype(np.float32)
    with torch.no_grad():
        params, _, _ = model(torch.from_numpy(inp))
    params = params.numpy()
    return {'R': params[0], 'L': params[1], 'C': params[2]}


def plot_response(freqs, target, generated, filter_type):
    plt.figure()
    plt.semilogx(freqs, 20 * np.log10(target + 1e-12), label='Target')
    plt.semilogx(freqs, 20 * np.log10(generated + 1e-12), label='Generated')
    plt.title(f'{filter_type} Filter Response')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.legend()
    plt.grid(True)
    plt.show()


def main(args):
    dummy_freqs = np.logspace(1, 6, num=200)
    input_dim = len(dummy_freqs) + 1
    model, freqs = load_model(args.model, input_dim, args.latent_dim)

    if args.filter_type not in FILTER_TYPES:
        raise ValueError(f"filter_type must be one of {FILTER_TYPES}")

    # For demo, generate a basic target response using nominal components
    target_params = {'R': args.R, 'L': args.L, 'C': args.C}
    if args.filter_type in ('bandpass', 'bandstop') and args.L == 0:
        raise ValueError(f"{args.filter_type} filter requires --L value")

    target = simulate_frequency_response(args.filter_type, target_params, freqs)
    design = design_circuit(model, target, args.filter_type)
    generated = simulate_frequency_response(args.filter_type, design, freqs)

    print('Generated component values:', design)
    plot_response(freqs, target, generated, args.filter_type)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate circuit from target frequency response')
    parser.add_argument('--model', type=str, default='model.pth')
    parser.add_argument('--filter-type', type=str, default='lowpass')
    parser.add_argument('--R', type=float, default=1e3)
    parser.add_argument('--L', type=float, default=1e-3)
    parser.add_argument('--C', type=float, default=1e-9)
    parser.add_argument('--latent-dim', type=int, default=16)
    args = parser.parse_args()
    main(args)
