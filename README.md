# Generative Circuit Synthesizer

This repository provides a research framework for training deep generative models that design analog filters.  Given a target frequency response, the model predicts component values for SPICE circuits which can be simulated using [PySpice](https://github.com/FabriceSalvaire/PySpice).  The code now supports offline dataset generation, an optional deeper VAE architecture and a new band‑stop filter type.

## Features

- Random circuit generation for low‑pass, high‑pass, band‑pass and band‑stop filters.
- Dataset generation with PySpice AC analysis and optional offline dataset export.
- Variational Autoencoder (VAE) and a deeper `AdvancedVAE` implemented in PyTorch.
- Training script with early stopping, progress bar and CSV logging.
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

You can also pre-generate a dataset to speed up experimentation:

```bash
python -m src.data.generate_dataset --num-samples 5000 --output dataset.npz
python -m src.train --dataset dataset.npz --model-type advanced --epochs 50 --output advanced.pth
```

Training logs are written to `metrics.csv` and early stopping is automatically applied.

### Inference

Use a trained model to design a circuit from a reference response:

```bash
python -m src.inference --model model.pth --filter-type lowpass --R 1000 --C 1e-9
```

Arguments `--R`, `--L`, `--C` specify nominal component values used to create the target frequency response. The script prints the generated component values and opens a plot comparing the target and generated Bode plots.

For band‑pass and band‑stop filters you must also provide a value for `--L`.

## Repository Structure

```
src/
  data/
    circuit_dataset.py   # dataset and simulation utilities
    generate_dataset.py  # create reusable datasets
  models/
    vae.py               # baseline VAE
    advanced_vae.py      # deeper VAE architecture
  train.py               # training script
  inference.py           # inference and visualization
requirements.txt
```

## Notes

This codebase is intended for educational use. The provided dataset generation routine is relatively slow due to PySpice simulations and is meant for small experiments. Feel free to extend the model or dataset generation for more complex filters and larger circuits.
The advanced model and larger datasets can quickly become computationally intensive so GPU acceleration is recommended when possible.
