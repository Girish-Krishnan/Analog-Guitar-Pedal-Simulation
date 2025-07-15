# Generative Circuit Synthesizer

This repository provides a simple research framework for training a deep generative model that designs analog filters. Given a target frequency response, the model predicts component values for SPICE circuits which can be simulated using [PySpice](https://github.com/FabriceSalvaire/PySpice).

## Features

- Random circuit generation for low‑pass, high‑pass and band‑pass filters.
- Dataset generation with PySpice AC analysis.
- Variational Autoencoder (VAE) implemented in PyTorch to map frequency responses to component values.
- Training script with configurable hyper‑parameters.
- Inference script that designs a circuit for a desired frequency response and plots Bode plots.

## Installation

1. Create a Python environment (Python 3.8+).
2. Install the required packages:

```bash
pip install -r requirements.txt
```

*PySpice requires a working NGSpice installation. See the [PySpice documentation](https://pyspice.fabrice-salvaire.fr/) for detailed setup instructions.*

## Usage

### Training

Generate a synthetic dataset and train the VAE:

```bash
python -m src.train --num-samples 1000 --epochs 20 --output model.pth
```

This saves `model.pth` containing the trained weights and frequency grid.

### Inference

Use a trained model to design a circuit from a reference response:

```bash
python -m src.inference --model model.pth --filter-type lowpass --R 1000 --C 1e-9
```

Arguments `--R`, `--L`, `--C` specify nominal component values used to create the target frequency response. The script prints the generated component values and opens a plot comparing the target and generated Bode plots.

For band‑pass filters, provide a value for `--L` as well.

## Repository Structure

```
src/
  data/
    circuit_dataset.py   # dataset and simulation utilities
  models/
    vae.py               # PyTorch VAE model
  train.py               # training script
  inference.py           # inference and visualization
requirements.txt
```

## Notes

This codebase is intended for educational use. The provided dataset generation routine is relatively slow due to PySpice simulations and is meant for small experiments. Feel free to extend the model or dataset generation for more complex filters and larger circuits.
