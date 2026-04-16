# model-diagnostics



## Install

```bash
pip install model-diagnostics
```

## Quick Start

```python
from model_diagnostics import maybe_attach_diagnostics

diag = maybe_attach_diagnostics(model)

for step, batch in enumerate(train_loader):
    loss = train_step(batch)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

    if diag and diag.should_stop(step, stop_after_steps=6):
        diag.print(f"{args.exp_dir}/diagnostics-step-{step}.txt")
        break
```