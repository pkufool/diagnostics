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

## CLI Tools

The package installs a `diagnostics` command with several subcommands for
post-processing diagnostics output. All tools support:

- Reading from a file or **stdin** (via pipe)
- Writing to a file with `-o`/`--output-file` (default: stdout)

### `diagnostics show_infinite`

Detect transitions to non-finite values (NaN/Inf). Prints lines containing
"finite" that follow lines NOT containing "finite" -- highlighting where
non-finite values first appear.

```bash
diagnostics show_infinite diagnostics.txt
cat diagnostics.txt | diagnostics show_infinite
```

### `diagnostics show_rms`

Extract the RMS of each module's output from diagnostics text.

```bash
diagnostics show_rms diagnostics.txt | sort -gr -k2 | head
```

### `diagnostics show_eigs`

Analyze eigenvalue statistics of module outputs. Computes ratios that indicate
how concentrated the variance is across eigen-directions (next-largest-ratio,
top_ratio, 2norm/1norm, etc.).

```bash
diagnostics show_eigs diagnostics.txt
```

### `diagnostics param_importance`

Compute a normalized importance score for each parameter. Importance is defined
as `value_mean * grad_mean * num_params`, aggregated by module name prefixes
and suffixes, and normalized so all scores sum to 1.0.

Two-file mode compares the importance outputs of two files and prints the ratio.

```bash
# Single file: analyze importance
diagnostics param_importance diagnostics.txt | sort -gr -k2 | head

# Two files: compare importance
diagnostics param_importance diag_epoch5.txt diag_epoch10.txt
```

### `diagnostics param_magnitude`

Extract the mean absolute value of each parameter from diagnostics text.

Two-file mode compares the magnitude outputs of two files and prints the ratio.

```bash
# Single file: extract magnitudes
diagnostics param_magnitude diagnostics.txt

# Two files: compare magnitudes
diagnostics param_magnitude diag_epoch5.txt diag_epoch10.txt
```

### `diagnostics compare_epochs`

Compare model parameters between two PyTorch checkpoints. For each float32
parameter, computes the RMS norm and normalized relative difference.

With `--summarize`, additionally aggregates the diffs by module name prefixes
and suffixes.

```bash
# Compare two checkpoints
diagnostics compare_epochs exp/epoch-5.pt exp/epoch-10.pt

# With hierarchical summary
diagnostics compare_epochs exp/epoch-5.pt exp/epoch-10.pt --summarize
```
