#!/usr/bin/env python3

import argparse
from pathlib import Path

import torch

from diagnostics import maybe_attach_diagnostics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-dir", type=str, default="./exp")
    args = parser.parse_args()

    model = torch.nn.Sequential(
        torch.nn.Linear(80, 128),
        torch.nn.ReLU(),
        torch.nn.Linear(128, 80),
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

    diag = maybe_attach_diagnostics(model)

    model.train()
    for step in range(100):
        x = torch.randn(8, 80)
        y = model(x)
        loss = (y**2).mean()

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if diag and diag.should_stop(step, stop_after_steps=6):
            out = Path(args.exp_dir) / f"diagnostics-step-{step}.txt"
            diag.print(out)
            print(f"Saved diagnostics to {out}")
            break


if __name__ == "__main__":
    main()
