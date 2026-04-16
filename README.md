# NN diagnostics

A useful tool to dump diagnostics info from checkpoint.

## Install

```bash
pip install nndiagnostics
```

## Quick Start

1. Integrate diagnostics in your training loop

```python
from diagnostics import maybe_attach_diagnostics

diag = maybe_attach_diagnostics(model)

for step, batch in enumerate(train_loader):
    loss = train_step(batch)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

    if diag and diag.should_stop(step, stop_after_steps=5):
        diag.print(f"{args.exp_dir}/diagnostics-step-{step}.txt")
        break
```

2. Dump diagnostics information (by setting env `DUMP_DIAGNOSTICS`)

```bash
DUMP_DIAGNOSTICS=1 python train.py
```
