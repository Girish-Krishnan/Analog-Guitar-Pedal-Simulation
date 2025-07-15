import argparse
import torch
from torch.utils.data import DataLoader
from src.data.circuit_dataset import CircuitDataset
from src.models.vae import VAE


def train(args):
    dataset = CircuitDataset(num_samples=args.num_samples)
    input_dim = len(dataset.freqs) + 1  # response + filter type
    model = VAE(input_dim=input_dim, latent_dim=args.latent_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model.train()
    for epoch in range(args.epochs):
        total_loss = 0
        for x, y in dataloader:
            optimizer.zero_grad()
            recon_y, mu, logvar = model(x)
            loss, recon_loss, kld = model.loss_function(recon_y, y, mu, logvar)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}: loss={total_loss/len(dataloader):.4f}")

    torch.save({'model_state_dict': model.state_dict(), 'freqs': dataset.freqs}, args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train generative circuit model')
    parser.add_argument('--num-samples', type=int, default=500)
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--latent-dim', type=int, default=16)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--output', type=str, default='model.pth')
    args = parser.parse_args()
    train(args)
