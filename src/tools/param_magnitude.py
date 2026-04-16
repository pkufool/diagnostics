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

"""Extract or compare parameter magnitudes from diagnostics output.

Single-file mode: extracts the mean absolute value of each parameter.
Two-file mode: compares the magnitude outputs of two files, printing
the value from each and their ratio.

Usage:
    diagnostics param_magnitude FILE [-o OUTPUT]
    diagnostics param_magnitude FILE1 FILE2 [-o OUTPUT]
"""

import argparse
import re

from tools.common import (
    add_output_arg,
    open_output,
)

_MAGNITUDE_RE = re.compile(
    r"^module=(?P<name>.+)\.param_value, dim=0, size=\d+, abs .+mean=(?P<mean>[^,]+),"
)


def register_subparser(subparsers):
    parser = subparsers.add_parser(
        "param_magnitude",
        help="Extract or compare parameter magnitudes.",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file1",
        type=str,
        help="First diagnostics file (or magnitude output for compare mode).",
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


def _parse_magnitude(filepath):
    """Parse a diagnostics file and extract mean abs value per parameter."""
    data = {}
    with open(filepath) as f:
        for line in f:
            m = _MAGNITUDE_RE.match(line.rstrip())
            if m:
                data[m.group("name")] = float(m.group("mean"))
    return data


def run(args):
    data1 = _parse_magnitude(args.file1)

    if args.file2 is not None:
        data2 = _parse_magnitude(args.file2)
        with open_output(args) as out:
            for k in sorted(data1.keys()):
                if k in data2:
                    v1 = data1[k]
                    v2 = data2[k]
                    ratio = v2 / v1
                    out.write(f"{k} {v1} {v2} {ratio}\n")
    else:
        with open_output(args) as out:
            for name in sorted(data1.keys()):
                out.write(f"{name} {data1[name]}\n")
