import argparse
import csv
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset, random_split
from tqdm import tqdm

from src.data.circuit_dataset import CircuitDataset
from src.models import VAE, AdvancedVAE


def load_saved_dataset(path):
    data = np.load(path)
    responses = data['responses']
    filter_types = data['filter_types'][:, None]
    x = np.concatenate([responses, filter_types], axis=1).astype(np.float32)
    y = data['params'].astype(np.float32)
    dataset = TensorDataset(torch.from_numpy(x), torch.from_numpy(y))
    freqs = data['freqs']
    return dataset, freqs


def build_datasets(args):
    if args.dataset:
        dataset, freqs = load_saved_dataset(args.dataset)
    else:
        ds = CircuitDataset(num_samples=args.num_samples)
        dataset = ds
        freqs = ds.freqs
    val_size = int(len(dataset) * 0.1)
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])
    return train_ds, val_ds, freqs


def train(args):
    train_ds, val_ds, freqs = build_datasets(args)
    input_dim = len(freqs) + 1
    if args.model_type == 'advanced':
        model = AdvancedVAE(input_dim=input_dim, latent_dim=args.latent_dim)
    else:
        model = VAE(input_dim=input_dim, latent_dim=args.latent_dim)

    device = (
        torch.device("cuda") if torch.cuda.is_available() else
        torch.device("mps") if torch.backends.mps.is_available() else
        torch.device("cpu")
    )
    print(f"Using device: {device}")
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size)

    best_val = float('inf')
    epochs_no_improve = 0

    with open(args.metrics, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['epoch', 'train_loss', 'val_loss'])
        for epoch in range(args.epochs):
            model.train()
            total_loss = 0.0
            for x, y in tqdm(train_loader, desc=f'Epoch {epoch+1}', leave=False):
                x, y = x.to(device), y.to(device)
                optimizer.zero_grad()
                recon_y, mu, logvar = model(x)
                loss, recon_loss, kld = model.loss_function(recon_y, y, mu, logvar)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            train_loss = total_loss / len(train_loader)

            # validation
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for x, y in val_loader:
                    x, y = x.to(device), y.to(device)
                    recon_y, mu, logvar = model(x)
                    loss, _, _ = model.loss_function(recon_y, y, mu, logvar)
                    val_loss += loss.item()
            val_loss /= len(val_loader)

            writer.writerow([epoch + 1, train_loss, val_loss])
            print(f"Epoch {epoch+1}: train={train_loss:.4f} val={val_loss:.4f}")

            if val_loss < best_val - 1e-6:
                best_val = val_loss
                epochs_no_improve = 0
                cpu_state = {k: v.cpu() for k, v in model.state_dict().items()}
                torch.save({'model_state_dict': cpu_state, 'freqs': freqs}, args.output)
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= args.patience:
                    print('Early stopping due to no improvement.')
                    break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train generative circuit model')
    parser.add_argument('--num-samples', type=int, default=500,
                        help='number of random circuits to generate if no dataset provided')
    parser.add_argument('--dataset', type=str, default='',
                        help='optional path to NPZ dataset generated with generate_dataset.py')
    parser.add_argument('--model-type', type=str, choices=['vae', 'advanced'], default='vae',
                        help='choose model architecture')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--latent-dim', type=int, default=16)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--patience', type=int, default=5,
                        help='early stopping patience')
    parser.add_argument('--metrics', type=str, default='metrics.csv',
                        help='CSV file to log losses')
    parser.add_argument('--output', type=str, default='model.pth')
    args = parser.parse_args()
    train(args)
