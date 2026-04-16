# diagnostics_usage_example

This directory shows minimal-intrusion integration in any training loop.

## Install package in editable mode

```bash
cd ../model-diagnostics-mini
pip install -e .
```

## Run sample

```bash
python train_loop_example.py --print-diagnostics 1 --exp-dir ./exp
```
