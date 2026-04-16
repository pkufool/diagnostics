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

"""Extract RMS of module outputs from diagnostics output.

Parses diagnostics text and extracts the RMS value of each module's
output, printing them sorted by module name.

Usage:
    diagnostics show_rms [FILE] [-o OUTPUT]
"""

import argparse
import re

from tools.common import add_output_arg, open_output

_OUTPUT_RE = re.compile(
    r"^module=(?P<name>.+)\.output(?:\[\d+\])?,"
    r" type=.+, dim=0, size=.+,"
    r" rms .+rms=(?P<rms>.+)$"
)


def register_subparser(subparsers):
    parser = subparsers.add_parser(
        "show_rms",
        help="Show RMS of each module's output.",
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
    value_rms = {}
    for line in args.file:
        m = _OUTPUT_RE.match(line.rstrip())
        if m:
            value_rms[m.group("name")] = float(m.group("rms"))

    with open_output(args) as out:
        for name in sorted(value_rms.keys()):
            out.write(f"{name} {value_rms[name]:.4g}\n")
