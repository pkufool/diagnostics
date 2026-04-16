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

"""Detect transitions to non-finite values (NaN/Inf) in diagnostics output.

Reads lines from a file or stdin. Prints any line that contains "finite"
and whose preceding line does NOT contain "finite" -- highlighting where
non-finite values first appear.

Usage:
    diagnostics show_infinite [FILE] [-o OUTPUT]
"""

import argparse

from tools.common import add_output_arg, open_output


def register_subparser(subparsers):
    parser = subparsers.add_parser(
        "show_infinite",
        help="Show first lines containing NaN/Inf values.",
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
    prev = ""
    with open_output(args) as out:
        for line in args.file:
            if "finite" in line and "finite" not in prev:
                out.write(line)
            prev = line
