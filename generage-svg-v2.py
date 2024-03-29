import argparse
import json
import logging
import math
import queue
import re
import sys
import os
from datetime import datetime

from typing import Any, Dict


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--diag-log",
        type=str,
        help="""The path to the diagnostics log.
        """,
    )
    parser.add_argument(
        "--ref-diag-log",
        type=str,
        help="""The path to the reference diagnostics log.
        """,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="""The path to the output svg.
        """,
    )
    parser.add_argument(
        "--scheme-type",
        type=str,
        default="output",
        help="""
        """,
    )
    parser.add_argument(
        "--scheme-attr",
        type=str,
        default="value",
        help="""
        """,
    )
    parser.add_argument(
        "--svg-width",
        type=int,
        default=1440,
        help="""The width of the generated svg.
        """,
    )
    parser.add_argument(
        "--svg-height",
        type=int,
        default=900,
        help="""The height of the generated svg.
        """,
    )
    return parser.parse_args()


def get_patterns():
    patterns = [
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), eigs percentiles: (?P<eigs>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), value percentiles: (?P<value>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), positive percentiles: (?P<positive>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), rms percentiles: (?P<rmsp>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), stddev percentiles: (?P<stddev>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), abs percentiles: (?P<abs>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), min percentiles: (?P<min>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), max percentiles: (?P<max>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), value percentiles: (?P<value>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), abs percentiles: (?P<abs>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), min percentiles: (?P<min>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), max percentiles: (?P<max>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), eigs percentiles: (?P<eigs>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), value percentiles: (?P<value>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), positive percentiles: (?P<positive>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), rms percentiles: (?P<rmsp>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), stddev percentiles: (?P<stddev>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), abs percentiles: (?P<abs>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), min percentiles: (?P<min>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), max percentiles: (?P<max>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), value percentiles: (?P<value>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), abs percentiles: (?P<abs>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), min percentiles: (?P<min>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), max percentiles: (?P<max>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), eigs (?P<eigs>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), value (?P<value>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), positive (?P<positive>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), rms (?P<rmsp>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), stddev (?P<stddev>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), abs (?P<abs>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), min (?P<min>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), max (?P<max>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), value (?P<value>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), abs (?P<abs>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), min (?P<min>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), max (?P<max>.*), norm=(?P<norm>\S+), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), eigs (?P<eigs>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), value (?P<value>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), positive (?P<positive>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), rms (?P<rmsp>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), stddev (?P<stddev>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), abs (?P<abs>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), min (?P<min>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), max (?P<max>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), value (?P<value>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), abs (?P<abs>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), min (?P<min>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
        "module=(?P<module>\S+), type=(?P<type>\S+), dim=(?P<dim>\d+), size=(?P<size>\S+), max (?P<max>.*), mean=(?P<mean>\S+), rms=(?P<rms>\S+)",
    ]

    patterns = [re.compile(p) for p in patterns]
    return patterns


# extract diagnostics info
def extract_diag_info(fname, patterns):
    matched_lines = []
    with open(fname, "r") as f:
        for line in f:
            match = None
            for p in patterns:
                match = p.match(line.strip())
                if match is not None:
                    matched_lines.append(match.groupdict())
                    break
    return matched_lines


# built structure
def build_structure(diag_lines):
    tree = {}
    for line in diag_lines:
        module = line["module"]
        attr = None
        for item in (
            "abs",
            "min",
            "max",
            "value",
            "rmsp",
            "stddev",
            "eigs",
            "positive",
        ):
            if item in line:
                attr = item
        assert attr is not None
        parts = module.split(".")
        node = tree
        for i, p in enumerate(parts):
            if i < len(parts) - 1:
                if p in node:
                    node = node[p]
                else:
                    node[p] = {}
                    node = node[p]
            else:
                if p not in node:
                    node[p] = [{attr: [line]}]
                else:
                    if attr in node[p][0]:
                        node[p][0][attr].append(line)
                    else:
                        node[p][0][attr] = [line]
    return tree


def get_width(node):
    if isinstance(node, list):
        return 1
    current = 0
    if "output" in node.keys():
        current = get_width(node["output"])
    child = 0
    for key in node.keys():
        if key in ("output", "grad", "output[0]"):
            continue
        child += get_width(node[key])
    node["length"] = max(current, child)
    return node["length"]


def inject_ref(tree, diag_lines):
    for line in diag_lines:
        module = line["module"]
        parts = module.split(".")
        node = tree
        for i, p in enumerate(parts):
            if i < len(parts) - 1:
                if p in node:
                    node = node[p]
                else:
                    break
            else:
                if p in node:
                    assert isinstance(node[p], list), node[p]
                    key = ""
                    for item in (
                        "abs",
                        "min",
                        "max",
                        "value",
                        "rmsp",
                        "stddev",
                        "eigs",
                        "positive",
                    ):
                        if item in line:
                            key = item
                            break
                    assert key != "", key
                    for item in node[p]:
                        if (
                            key in item
                            and item["module"] == module
                            and item["dim"] == line["dim"]
                        ):
                            for m in ("rms", "mean", "norm", key, "size"):
                                if m in item and m in line:
                                    item[f"{m}_ref"] = line[m]


def add_javascripts():
    svg = f"""
    <script type="text/ecmascript">
    <![CDATA[
    """
    with open("script.js", "r") as f:
        for line in f:
            svg += line

    svg += f""" ]]>
    </script>
    """
    return svg


def write_svg(
    svg_height: int,
    svg_width: int,
    svg_title: str,
    tree: Dict[str, Any],
    scheme_type: str,
    scheme_attr: str,
    output: str,
    font_family: str = "Verdana",
):
    svg = f"""<?xml version="1.0" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg version="1.1" width="{svg_width}" height="{svg_height}" onload="init(evt)" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    """
    svg += """
    <defs >
        <linearGradient id="background" y1="0" y2="1" x1="0" x2="0" >
            <stop stop-color="#eeeeee" offset="5%" />
            <stop stop-color="#eeeeb0" offset="95%" />
        </linearGradient>
    </defs>
    <style type="text/css">
        .rect_g {stroke: white; stroke-width: 1; pointer-events: all;}
        .rect_g:hover { cursor:pointer; }
        .color_g:hover {stroke:red; stroke-width:0.5; cursor:pointer; }
    </style>
    """

    svg += add_javascripts()

    svg += f"""
    <rect x="0.0" y="0" width="{svg_width}" height="{svg_height}" fill="url(#background)"  />

    <text text-anchor="" x="10.00" y="24" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" id="unzoom" onclick="unzoom()" style="opacity:0.0;cursor:pointer" >Reset Zoom</text>

    <text text-anchor="middle" x="{svg_width / 2}" y="48" font-size="18" font-family="{font_family}" font-weight="bold" fill="rgb(0,0,0)">{svg_title}</text>

    <text id="current_color" text-anchor="" x="10" y="100" font-size="12" font-family="{font_family}" style="display:none" >{scheme_type} {scheme_attr}</text>

    <text text-anchor="" x="10" y="100" font-size="12" font-family="{font_family}" font-weight="bold" fill="rgb(0,0,0)" >Color Scheme:</text>
    <text class="color_g" style="opacity: 1.0" onclick="update_color('output')" id="color_output" text-anchor="" x="115" y="100" font-size="12" font-family="{font_family}" fill="red" >Output/Weight</text>
    <text class="color_g" style="opacity: 0.5" onclick="update_color('grad')" id="color_grad" text-anchor="" x="210" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >Gradient</text>
    <text text-anchor="" x="278" y="100" font-size="12" font-family="{font_family}" font-weight="bold" fill="rgb(0,0,0)" >|</text>

    <text class="color_g" style="opacity: 0.5" onclick="update_color('value')" id="color_value" text-anchor="" x="291" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >value</text>
    <text class="color_g" style="opacity: 1.0" onclick="update_color('abs')" id="color_abs" text-anchor="" x="331" y="100" font-size="12" font-family="{font_family}" fill="red" >abs</text>
    <text class="color_g" style="opacity: 0.5" onclick="update_color('max')" id="color_max" text-anchor="" x="363" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >max</text>
    <text class="color_g" style="opacity: 0.5" onclick="update_color('min')" id="color_min" text-anchor="" x="395" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >min</text>
    <text class="color_g" style="opacity: 0.5" onclick="update_color('positive')" id="color_positive" text-anchor="" x="427" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >positive</text>
    <text class="color_g" style="opacity: 0.5" onclick="update_color('rmsp')" id="color_rmsp" text-anchor="" x="485" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >rms</text>
    <text class="color_g" style="opacity: 0.5" onclick="update_color('stddev')" id="color_stddev" text-anchor="" x="520" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >stddev</text>
    <text class="color_g" style="opacity: 0.5" onclick="update_color('eigs')" id="color_eigs" text-anchor="" x="570" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >eigs</text>

    <text text-anchor="" x="{svg_width - 120}" y="24" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" id="search" onmouseover="searchover()" onmouseout="searchout()" onclick="search_prompt()" style="opacity:0.1;cursor:pointer" >Search</text>
    <text text-anchor="" x="{svg_width-120}" y="{svg_height-15}" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" id="matched" > </text>
    <text text-anchor="" x="10.00" y="{svg_height-15}" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" style="display:none" id="details" > </text>
    """

    svg += add_model(
        svg_height=svg_height,
        svg_width=svg_width,
        tree=tree,
        scheme_type=scheme_type,
        scheme_attr=scheme_attr,
    )

    svg += """
    </svg>
    """

    with open(output, "w") as f:
        f.write(svg)


def add_dim(
    x: float,
    y: float,
    width: float,
    ratio: float,
    dim: int,
    attributes: Dict[str, Any],
    scheme_type: str,
    scheme_attr: str,
    cell_height: float,
):
    """
    attributes: {
      "output": {"abs" : "", "value": ""...},
      "grad" : {"abs" : "", ...},
      "module_type": "",
      "module": ""
    }
    """
    metric = ""
    if scheme_type in attributes and scheme_attr in attributes[scheme_type]:
        # 0: percentiles
        # 1: mean
        # 2: rms
        # 3: norm
        attrs = attributes[scheme_type][scheme_attr].split("|")
        metric += (
            f" dim[{dim}] {scheme_attr} percentiles: [{attrs[0]}], "
            f"mean: {attrs[1]}, rms: {attrs[2]},"
        )
        if len(attrs) == 4:
            metric += f" norm: {attrs[3]}"
        attr_values = [float(x) for x in attrs[0].split(" ")]
    else:
        attr_values = [0] * 11

    module_name = ""
    if attributes["module"] != "":
        module_name = attributes["module"] + "." + scheme_type
    info_text = (
        module_name
        if attributes["module_type"] == ""
        else module_name + f" ({attributes['module_type']})"
    )

    info_text += metric

    svg = ""
    min_value = attr_values[0]
    max_value = attr_values[-1]
    if len(attr_values) != 11:
        attr_values = attr_values + [0] * (11 - len(attr_values))
    for i in range(11):
        y1 = y - (i + 1) * cell_height
        av = attr_values[i]
        negative = False
        if av == 0:
            lv = 127
        else:
            if av < 0:
                negative = True
            if negative:
                lv = 0 if av == min_value else (av - min_value) / (0 - min_value)
                lv = int((1 - lv) * 80 + 180)
            else:
                lv = 80 - int(av / max_value * 80)
        color = f"hsl({lv}, 100%, 50%)"
        svg += f"""<rect x="{x}" y="{y1}" ratio="{ratio}" width="{width}" height="{cell_height}" fill="{color}" rx="0" ry="0" />"""

    svg += f"""
      <rect class="rect_g" x="{x}" y="{y - cell_height * 11}" width="{width}" height="{cell_height * 11}" fill="transparent" rx="2" ry="2" dim="{dim}" ratio="{ratio}" onclick="zoom(this)" """
    for t in ("output", "grad"):
        for k in attributes[t]:
            svg += f"""{t}_{k}="{attributes[t][k]}" """
    svg += f"><title>{info_text}</title></rect>"
    return svg


def add_module(
    node: Dict[str, Any],
    attributes: Dict[str, Any],
    scheme_type: str,
    scheme_attr: str,
    color_type: str,
    cell_height: float,
):
    """
    attributes: {"output" : [{"abs" : ""}], "module_type" : "", "module" : ""}
    """
    x, y, width, text = node["x"], node["y"], node["width"], node["text"]

    if text == "<top-level>":
        text = "top-level"

    svg = f"""
      <g class="module_g" onclick="zoom(this)"><title>{text}</title>
      """
    # module don't have diagnostics info
    if len(attributes["output"]) == 0:
        # return the module group
        color = f"hsl(127, 100%, 50%)"
        svg += f"""<rect x="{x}" y="{y}" width="{width}" height="{cell_height * 11}" fill="{color}" rx="2" ry="2" />"""
        svg += "</g>"
        return svg

    # draw dimensions
    dims = len(attributes["output"])
    sub_width = width / dims
    ratio = 1 / dims
    logging.info(
        f"output len : {len(attributes['output'])}, grad len : {len(attributes['grad'])}, module : {attributes['module']}"
    )
    grad_dims = len(attributes["grad"])

    logging.info(f"attributes : {attributes}\n")
    for i in range(len(attributes["output"])):
        x1 = x + i * sub_width
        sub_attributes = {
            "output": attributes["output"][i],
            "grad": attributes["grad"][i]
            if i < grad_dims
            else {},  # some modules don't have grad
            "module": attributes["module"],
            "module_type": attributes["module_type"],
        }
        svg += add_dim(
            x=x1,
            y=y,
            width=sub_width,
            ratio=ratio,
            dim=i,
            attributes=sub_attributes,
            scheme_type=scheme_type,
            scheme_attr=scheme_attr,
            cell_height=cell_height,
        )
    svg += "</g>"
    return svg


def add_model(
    svg_height: int,
    svg_width: int,
    tree: Dict[str, Any],
    scheme_type: str,
    scheme_attr: str,
    color_type: str = "hsl",
    cell_height: float = 6.5,
):
    bfs_node = {
        "x": 10,
        "y": svg_height - 5,
        "width": svg_width - 20,
        "text": "root",
        "node": tree,
    }

    bfs_queue = queue.Queue()
    bfs_queue.put(bfs_node)
    total_length = tree["length"]
    default_scheme = {"type": scheme_type, "attr": scheme_attr}

    svg = ""
    while not bfs_queue.empty():
        node = bfs_queue.get()
        keys = node["node"].keys()
        children = [
            x
            for x in keys
            if (
                x
                not in [
                    "output",
                    "output[0]",
                    "output[1]",
                    "grad",
                    "param_value",
                    "param_grad",
                    "length",
                ]
            )
        ]

        attributes = {"output": [], "grad": [], "module": "", "module_type": ""}
        if "output" in keys or "param_value" in keys:
            assert ("output" in keys and "param_value" not in keys) or (
                "output" not in keys and "param_value" in keys
            ), keys

            for k in (
                "output",
                "grad",
                "param_value",
                "param_grad",
            ):
                if k not in keys:
                    continue

                assert "abs" in node["node"][k][0], node["node"][k][0].keys()
                dims = len(node["node"][k][0]["abs"])
                if k == "output" or k == "param_value":
                    attributes["output"] = [{} for _ in range(dims)]
                    module_name = node["node"][k][0]["abs"][0]["module"]
                    module_name = ".".join(module_name.split(".")[0:-1])
                    attributes["module"] = module_name
                    if "type" in node["node"][k][0]["abs"][0]:
                        attributes["module_type"] = node["node"][k][0]["abs"][0]["type"]
                else:
                    attributes["grad"] = [{} for _ in range(dims)]

                for attr in (
                    "abs",
                    "max",
                    "min",
                    "value",
                    "positive",
                    "rmsp",
                    "stddev",
                    "eigs",
                ):
                    if attr not in node["node"][k][0]:
                        continue

                    items = node["node"][k][0][attr]
                    tk = k
                    tattr = attr
                    for item in items:
                        dim = int(item["dim"])
                        attr_value = f"{item[attr][1:-1]}|{item['mean']}|{item['rms']}"
                        if "norm" in item:
                            attr_value += f"|{item['norm']}"
                        if attr == "rmsp":
                            tattr = "rms"
                        if k == "param_value":
                            tk = "output"
                        if k == "param_grad":
                            tk = "grad"
                        logging.info(
                            f"k : {tk}, attr : {tattr} dim : {dim}, attr_value : {attr_value}"
                        )
                        attributes[tk][dim][tattr] = attr_value

        # module here means an output or a weight module.
        svg += add_module(
            node=node,
            attributes=attributes,
            scheme_type=scheme_type,
            scheme_attr=scheme_attr,
            color_type=color_type,
            cell_height=cell_height,
        )

        if len(children) == 0:
            continue

        x, y, width, text = node["x"], node["y"], node["width"], node["text"]
        offset = 0
        for i, child in enumerate(children):
            logging.info(f"child : {child}")
            child_width = (
                node["node"][child]["length"] / total_length * (svg_width - 20)
            )
            child_node = {
                "x": x + offset,
                "y": y - cell_height * 11,
                "width": child_width,
                "text": child if node["text"] == "root" else f"{node['text']}.{child}",
                "node": node["node"][child],
            }
            offset += child_width
            bfs_queue.put(child_node)
    return svg


def main():
    args = get_args()
    tree = build_structure(extract_diag_info(args.diag_log, get_patterns()))

    get_width(tree)

    logging.info(json.dumps(tree, indent=2))

    has_ref = False
    if args.ref_diag_log is not None:
        inject_ref(tree, extract_diag_info(args.ref_diag_log, get_patterns()))
        has_ref = True

    svg_width = 1440 if args.svg_width < 1440 else args.svg_width
    svg_height = args.svg_height

    svg_title = "Differential Diagnostics" if has_ref else "Diagnostics"

    write_svg(
        svg_height=svg_height,
        svg_width=svg_width,
        svg_title=svg_title,
        tree=tree,
        scheme_type=args.scheme_type,
        scheme_attr=args.scheme_attr,
        output=args.output,
    )


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    now = datetime.now()
    data_time = now.strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs("logs", exist_ok=True)
    log_file_name = f"logs/generate_svg_{data_time}"
    logging.basicConfig(
        level=logging.INFO,
        format=formatter,
        handlers=[logging.FileHandler(log_file_name), logging.StreamHandler()],
    )

    main()
