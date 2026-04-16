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

"""Extract or compare parameter importance from diagnostics output.

Single-file mode: computes a normalized importance score for each parameter
(importance = value_mean * grad_mean * num_params), aggregates by module
name prefixes and suffixes, and normalizes so all scores sum to 1.0.

Two-file mode: compares the importance outputs of two files, printing
the value from each and their ratio.

Usage:
    diagnostics param_importance FILE [-o OUTPUT]
    diagnostics param_importance FILE1 FILE2 [-o OUTPUT]
"""

import argparse
import re

from tools.common import (
    add_output_arg,
    aggregate_by_prefix_suffix,
    open_output,
)

_VALUE_MEAN_RE = re.compile(
    r"^module=(?P<name>.+)\.param_value, dim=0, size=\d+, abs .+mean=(?P<mean>[^,]+),"
)
_GRAD_MEAN_RE = re.compile(
    r"^module=(?P<name>.+)\.param_grad, dim=0, size=\d+, abs .+mean=(?P<mean>[^,]+),"
)
_NUM_PARAMS_RE = re.compile(
    r"^module=(?P<name>.+)\.param_value, dim=(?P<dim>\d+), size=(?P<size>\d+), abs .+mean="
)


def _parse_importance(filepath):
    """Parse a diagnostics file and compute raw importance per parameter."""
    value_mean = {}
    grad_mean = {}
    num_params = {}
    seen_dims = set()

    with open(filepath) as f:
        for line in f:
            line = line.rstrip()

            m = _VALUE_MEAN_RE.match(line)
            if m:
                value_mean[m.group("name")] = float(m.group("mean"))

            m = _GRAD_MEAN_RE.match(line)
            if m:
                grad_mean[m.group("name")] = float(m.group("mean"))

            m = _NUM_PARAMS_RE.match(line)
            if m:
                name = m.group("name")
                dim = int(m.group("dim"))
                size = int(m.group("size"))
                key = (name, dim)
                if key not in seen_dims:
                    seen_dims.add(key)
                    if name not in num_params:
                        num_params[name] = 1
                    num_params[name] *= size

    importance = {}
    for name, v in value_mean.items():
        g = grad_mean.get(name, 0.0)
        n = num_params.get(name, 0)
        importance[name] = v * g * n

    return importance


def register_subparser(subparsers):
    parser = subparsers.add_parser(
        "param_importance",
        help="Extract or compare parameter importance.",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file1",
        type=str,
        help="First diagnostics file (or importance output for compare mode).",
    )
    parser.add_argument(
        "file2",
        type=str,
        nargs="?",
        default=None,
        help="Second file for comparison. If provided, compares the two files.",
    )
    add_output_arg(parser)
    parser.set_defaults(func=run)


def _compute_normalized_importance(filepath):
    """Parse a diagnostics file and return normalized importance per param."""
    importance = _parse_importance(filepath)
    total = sum(importance.values())
    if total == 0:
        total = 1.0
    aggregated = aggregate_by_prefix_suffix(importance)
    return {k: v / total for k, v in aggregated.items()}


def run(args):
    if args.file2 is not None:
        data1 = _compute_normalized_importance(args.file1)
        data2 = _compute_normalized_importance(args.file2)
        with open_output(args) as out:
            for k in sorted(data1.keys()):
                if k in data2:
                    v1 = data1[k]
                    v2 = data2[k]
                    ratio = v2 / v1
                    out.write(f"{k} {v1} {v2} {ratio}\n")
    else:
        data = _compute_normalized_importance(args.file1)
        with open_output(args) as out:
            for k in sorted(data.keys()):
                out.write(f"{k} {data[k]:.4g}\n")
