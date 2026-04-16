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

"""Analyze eigenvalue statistics of module outputs from diagnostics output.

Parses eigenvalue lines from diagnostics text and computes derived ratios
that indicate how concentrated the variance is across eigen-directions.

Usage:
    diagnostics show_eigs [FILE] [-o OUTPUT]
"""

import argparse
import re

from tools.common import add_output_arg, open_output

_VALUE_RE = re.compile(r", size=.+, value.*norm=(\S+),")
_ABS_RE = re.compile(r", size=(\d+), abs.*mean=(\S+),")
_EIGS_RE = re.compile(
    r"^module=(\S+),.+"
    r"(dim=.+, size=.+),"
    r" eigs .+ (\S+) (\S+) (\S+)\],"
    r" norm=(\S+), mean=(\S+), rms=(\S+)"
)


def register_subparser(subparsers):
    parser = subparsers.add_parser(
        "show_eigs",
        help="Show eigenvalue analysis of module outputs.",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        type=argparse.FileType("r"),
        help="Diagnostics file to read (default: stdin).",
    )
    add_output_arg(parser)
    parser.set_defaults(func=run)


def run(args):
    value_norm = 0.0
    one_norm = 1.0e-20
    size = 1

    with open_output(args) as out:
        for line in args.file:
            # Track value norm from value lines
            m = _VALUE_RE.search(line)
            if m:
                value_norm = float(m.group(1))

            # Track size and one_norm from abs lines
            m = _ABS_RE.search(line)
            if m:
                size = int(m.group(1))
                abs_mean = float(m.group(2))
                one_norm = max(size * abs_mean, 1.0e-20)

            # Process eigenvalue lines
            m = _EIGS_RE.search(line)
            if m:
                module = m.group(1)
                dim_and_size = m.group(2)
                next_next_largest_eig = float(m.group(3))
                next_largest_eig = float(m.group(4))
                largest_eig = float(m.group(5))
                eigs_norm = float(m.group(6))
                eig_mean = float(m.group(7))
                eig_rms = float(m.group(8))

                if eigs_norm == 0:
                    out.write(f"WARN: eigs_norm = 0: {line.rstrip()}\n")
                    continue

                norm_ratio = (eig_rms * size) / one_norm
                rms_over_mean = eig_rms / eig_mean if eig_mean != 0 else 0.0

                if eigs_norm - value_norm > 0:
                    denom = eigs_norm - value_norm
                    next_next_largest_ratio = next_next_largest_eig / denom
                    next_largest_ratio = next_largest_eig / denom
                else:
                    next_next_largest_ratio = 0.0
                    next_largest_ratio = 0.0

                mean_ratio = value_norm / eigs_norm
                top_ratio = largest_eig / eigs_norm

                out.write(
                    f"module={module}, {dim_and_size},"
                    f" norm={eigs_norm},"
                    f" next-next-largest-ratio={next_next_largest_ratio:.4g},"
                    f" next-largest-ratio={next_largest_ratio:.4g},"
                    f" mean_ratio={mean_ratio:.4g},"
                    f" 2norm/1norm={norm_ratio:.4g},"
                    f" top_ratio={top_ratio:.4g},"
                    f" rms_over_mean={rms_over_mean:.4g}\n"
                )
