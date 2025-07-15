import argparse
import numpy as np
from src.data.circuit_dataset import CircuitDataset


def main(args):
    dataset = CircuitDataset(num_samples=args.num_samples)
    responses = np.stack([s['response'] for s in dataset.samples])
    params = np.stack([s['params'] for s in dataset.samples])
    filter_types = np.array([s['filter_type'] for s in dataset.samples])
    np.savez(args.output, responses=responses, params=params,
             filter_types=filter_types, freqs=dataset.freqs)
    print(f"Saved {len(dataset)} samples to {args.output}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate dataset of circuit responses')
    parser.add_argument('--num-samples', type=int, default=1000,
                        help='number of circuits to simulate')
    parser.add_argument('--output', type=str, default='dataset.npz',
                        help='output NPZ file')
    args = parser.parse_args()
    main(args)
