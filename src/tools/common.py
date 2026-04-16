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

import argparse
import io
import sys
from contextlib import contextmanager
from typing import Dict, IO, Optional


def add_output_arg(parser: argparse.ArgumentParser) -> None:
    """Add -o/--output-file to a parser. All tools share this."""
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        default=None,
        help="Output file path. If not specified, prints to stdout.",
    )


@contextmanager
def open_output(args):
    """Context manager yielding a writable file object.

    If args.output_file is None, yields sys.stdout.
    Otherwise opens the file and yields the handle.
    """
    if args.output_file is not None:
        f = open(args.output_file, "w")
        try:
            yield f
        finally:
            f.close()
    else:
        yield sys.stdout


def compare_two_key_value_files(
    path1: str, path2: str
) -> list:
    """Read two files of 'key value' lines. For each key present in both,
    compute ratio = value2 / value1. Returns list of (key, v1, v2, ratio)."""
    f1 = {}
    with open(path1) as fh:
        for line in fh:
            parts = line.strip().split()
            if len(parts) >= 2:
                f1[parts[0]] = float(parts[1])

    f2 = {}
    with open(path2) as fh:
        for line in fh:
            parts = line.strip().split()
            if len(parts) >= 2:
                f2[parts[0]] = float(parts[1])

    results = []
    for k in sorted(f1.keys()):
        if k in f2:
            v1 = f1[k]
            v2 = f2[k]
            ratio = v2 / v1
            results.append((k, v1, v2, ratio))
    return results


def aggregate_by_prefix_suffix(data: Dict[str, float]) -> Dict[str, float]:
    """Aggregate a dict of {dot.separated.name: value} into a dict that
    also includes prefix aggregates (e.g. 'encoder', 'encoder.layers')
    and suffix aggregates (e.g. '*.layers.0').

    Used by both param_importance and compare_epochs --summarize.
    """
    all_data = {}

    # Prefix aggregation: for each key, add its value to all prefix paths
    for k, v in data.items():
        parts = k.split(".")
        prefix = ""
        for i, part in enumerate(parts):
            prefix = part if i == 0 else f"{prefix}.{part}"
            all_data[prefix] = all_data.get(prefix, 0.0) + v

    # Copy to preserve prefix results for suffix aggregation
    prefix_data = dict(all_data)

    # Suffix aggregation: for each prefix-key, add to *.suffix paths
    for k, n in prefix_data.items():
        parts = k.split(".")
        suffix = ""
        for i in range(len(parts) - 1, 0, -1):
            suffix = parts[i] if i == len(parts) - 1 else f"{parts[i]}.{suffix}"
            key = f"*.{suffix}"
            all_data[key] = all_data.get(key, 0.0) + n

    return all_data


def aggregate_by_prefix_suffix_with_count(
    data: Dict[str, float],
) -> tuple:
    """Like aggregate_by_prefix_suffix but also tracks counts for averaging.

    Returns (agg_sum, agg_count) where both are dicts.
    Used by compare_epochs --summarize.
    """
    agg_sum = {}
    agg_count = {}

    for k, v in data.items():
        parts = k.split(".")
        prefix = ""
        for i, part in enumerate(parts):
            prefix = part if i == 0 else f"{prefix}.{part}"
            agg_sum[prefix] = agg_sum.get(prefix, 0.0) + v
            agg_count[prefix] = agg_count.get(prefix, 0) + 1

    prefix_sum = dict(agg_sum)
    prefix_count = dict(agg_count)

    for k in prefix_sum:
        parts = k.split(".")
        suffix = ""
        n = prefix_count[k]
        for i in range(len(parts) - 1, 0, -1):
            suffix = parts[i] if i == len(parts) - 1 else f"{parts[i]}.{suffix}"
            key = f"*.{suffix}"
            agg_sum[key] = agg_sum.get(key, 0.0) + prefix_sum[k]
            agg_count[key] = agg_count.get(key, 0) + n

    return agg_sum, agg_count
