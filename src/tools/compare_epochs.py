# Copyright       2026  Xiaomi Corp.       (authors: Daniel Povey,
#                                                    Wei Kang)
#
# See ../LICENSE for clarification regarding multiple authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Compare model parameters between two epochs/checkpoints.

Loads two PyTorch checkpoints, compares the float32 parameters by computing
RMS norm and normalized relative difference.

Optionally with --summarize, aggregates the differences by module name
prefixes and suffixes.

Usage:
    diagnostics compare_epochs CHECKPOINT1 CHECKPOINT2 [-o OUTPUT] [--summarize]
"""

import argparse
import re

import torch

from tools.common import (
    add_output_arg,
    aggregate_by_prefix_suffix_with_count,
    open_output,
)

_DIFF_RE = re.compile(r"^For (.+), rms=.+\[diff=(.+)\]$")


def _normalize(x):
    return x / ((x**2).mean().sqrt())


def _summarize_diffs(lines):
    """Aggregate diff values by module name prefix/suffix hierarchy."""
    diff_data = {}
    for line in lines:
        line = line.strip()
        m = _DIFF_RE.match(line)
        if m:
            name = m.group(1)
            diff = float(m.group(2))
            diff_data[name] = diff

    if not diff_data:
        return []

    agg_sum, agg_count = aggregate_by_prefix_suffix_with_count(diff_data)
    results = []
    for k in sorted(agg_sum.keys()):
        avg = agg_sum[k] / agg_count[k] if agg_count[k] > 0 else 0.0
        results.append((k, avg))
    return results


def register_subparser(subparsers):
    parser = subparsers.add_parser(
        "compare_epochs",
        help="Compare model parameters between two checkpoints.",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "checkpoint1",
        type=str,
        help="Path to the first checkpoint (.pt file).",
    )
    parser.add_argument(
        "checkpoint2",
        type=str,
        help="Path to the second checkpoint (.pt file).",
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Also print aggregated diffs by module name prefix/suffix.",
    )
    add_output_arg(parser)
    parser.set_defaults(func=run)


def run(args):
    a = torch.load(args.checkpoint1, map_location="cpu", weights_only=False)
    b = torch.load(args.checkpoint2, map_location="cpu", weights_only=False)

    try:
        a = a["model"]
        b = b["model"]
    except KeyError:
        pass

    lines = []
    for k in a.keys():
        v_old = a[k].clone()
        v_new = b[k].clone()
        if v_old.dtype == torch.float32:
            norm = ((v_old**2).sum() / v_old.numel()).sqrt()
            rel_diff = ((_normalize(v_new) - _normalize(v_old)) ** 2).mean().sqrt()
            if v_old.numel() == 1:
                s = f"For {k}, value={v_old.item():.2g}->{v_new.item():.2g}"
            else:
                s = f"For {k}, rms={norm:.2g}[diff={rel_diff:.2g}]"
            lines.append(s)

    with open_output(args) as out:
        for line in lines:
            out.write(line + "\n")

        if args.summarize:
            results = _summarize_diffs(lines)
            out.write("\n# Aggregated diffs by module group\n")
            for k, avg in results:
                out.write(f"{k} {avg:.4g}\n")
