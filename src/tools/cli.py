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

"""Command-line interface for nndiagnostics analysis tools.

Usage:
    diagnostics show_infinite [FILE] [-o OUTPUT]
    diagnostics show_rms [FILE] [-o OUTPUT]
    diagnostics show_eigs [FILE] [-o OUTPUT]
    diagnostics param_importance FILE [FILE2] [-o OUTPUT]
    diagnostics param_magnitude FILE [FILE2] [-o OUTPUT]
    diagnostics compare_epochs CHECKPOINT1 CHECKPOINT2 [--summarize] [-o OUTPUT]
"""

import argparse

from tools import (
    show_infinite,
    show_rms,
    show_eigs,
    param_importance,
    param_magnitude,
    compare_epochs,
)


def main():
    parser = argparse.ArgumentParser(
        prog="diagnostics",
        description="PyTorch tensor diagnostics analysis tools.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_infinite.register_subparser(subparsers)
    show_rms.register_subparser(subparsers)
    show_eigs.register_subparser(subparsers)
    param_importance.register_subparser(subparsers)
    param_magnitude.register_subparser(subparsers)
    compare_epochs.register_subparser(subparsers)

    args = parser.parse_args()
    args.func(args)
