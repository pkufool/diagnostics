import re
import sys
import json
import queue
import math


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
                    node[p] = [line]
                else:
                    node[p].append(line)
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


tree = build_structure(extract_diag_info(sys.argv[1], get_patterns()))

get_width(tree)

has_ref = False
if len(sys.argv) == 4:
    inject_ref(tree, extract_diag_info(sys.argv[3], get_patterns()))
    has_ref = True

print(json.dumps(tree, indent=2))

svg_width = 1900
svg_height = 900
svg_title = "Differential Diagnostics" if has_ref else "Diagnostics"
font_family = "Verdana"

# write svg
svg_head = f"""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" width="{svg_width}" height="{svg_height}" onload="init(evt)" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
"""
svg_head += """
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
<script type="text/ecmascript">
<![CDATA[
"""

with open("script.js", "r") as f:
    for line in f:
        svg_head += line

svg_head += f""" ]]>
</script>
"""

svg_head += f"""
<rect x="0.0" y="0" width="{svg_width}" height="{svg_height}" fill="url(#background)"  />
<text text-anchor="" x="10.00" y="24" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" id="unzoom" onclick="unzoom()" style="opacity:0.0;cursor:pointer" >Reset Zoom</text>
<text text-anchor="middle" x="{svg_width / 2}" y="48" font-size="18" font-family="{font_family}" font-weight="bold" fill="rgb(0,0,0)">{svg_title}</text>
<text id="current_color" text-anchor="" x="10" y="100" font-size="12" font-family="{font_family}" style="display:none" >output mean abs</text>
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
default_scheme = {"type": "output", "attr": "value", "metric": "mean"}
color_type = "hsl"  # rgb

with open(sys.argv[2], "w") as f:
    f.write(svg_head)
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
                    "grad",
                    "param_value",
                    "param_grad",
                    "length",
                ]
            )
        ]

        attributes = {"output": {}, "grad": {}, "module": "", "module_type": ""}
        if "output" in keys or "param_value" in keys:
            assert ("output" in keys and "param_value" not in keys) or (
                "output" not in keys and "param_value" in keys
            ), keys

            for k in ("output", "grad", "param_value", "param_grad"):
                if k not in keys:
                    continue
                module_name = node["node"][k][0]["module"]
                module_name = ".".join(module_name.split(".")[0:-1])
                attributes["module"] = module_name
                if "type" in node["node"][k][0]:
                    attributes["module_type"] = node["node"][k][0]["type"]
                for item in node["node"][k]:
                    for attr in (
                        "abs",
                        "max",
                        "min",
                        "value",
                        "positive",
                        "rmsp",
                        "stddev",
                        "eigs",
                        "abs_ref",
                        "max_ref",
                        "min_ref",
                        "value_ref",
                        "positive_ref",
                        "rmsp_ref",
                        "stddev_ref",
                        "eigs_ref",
                    ):
                        if attr in item and item["dim"] == "0":
                            if attr.endswith("ref"):
                                attr_value = f"{item[attr][1:-1]} {item['mean_ref']} {item['rms_ref']} {item['size_ref']}"
                            else:
                                attr_value = f"{item[attr][1:-1]} {item['mean']} {item['rms']} {item['size']}"
                            if "norm" in item:
                                if attr.endswith("ref"):
                                    attr_value += f" {item['norm_ref']}"
                                else:
                                    attr_value += f" {item['norm']}"
                            if attr == "rmsp":
                                attr = "rms"
                            if attr == "rmsp_ref":
                                attr = "rms_ref"
                            if k == "param_value":
                                k = "output"
                            if k == "param_grad":
                                k = "grad"
                            attributes[k][attr] = attr_value
        height = 6.5
        x, y, width, text = node["x"], node["y"], node["width"], node["text"]
        metric = ""
        if (
            default_scheme["type"] in attributes
            and default_scheme["attr"] in attributes[default_scheme["type"]]
        ):
            attrs = attributes[default_scheme["type"]][default_scheme["attr"]].split(
                " "
            )
            metric += (
                f" {default_scheme['attr']} percentiles: [{' '.join(attrs[0:11])}], "
                f"mean: {attrs[11]}, rms: {attrs[12]},"
            )
            if len(attrs) == 15:
                metric += f" norm: {attrs[14]}"
            attr_values = [float(x) for x in attrs[0:11]]
        else:
            attr_values = [0] * 11

        module_name = ""
        if attributes["module"] != "":
            module_name = attributes["module"] + "." + default_scheme["type"]
        info_text = (
            module_name
            if attributes["module_type"] == ""
            else module_name + f" ({attributes['module_type']})"
        )

        info_text += metric
        if info_text == "":
            info_text = text

        g = f"""
          <g class="module_g" onmouseover="s('{text}')" onmouseout="c()" onclick="zoom(this)"><title>{info_text}</title>
          """

        for i in range(11):
            y1 = y - (i + 1) * height
            av = attr_values[i]
            negative = False
            if av == 0:
                rv, gv, bv = 255, 255, 255
                lv = 127
            else:
                if av < 0:
                    negative = True
                    av = -av
                rv = math.sin(math.log(av) * (2 * math.pi / math.log(10)))
                rv = int((0.5 + 0.5 * rv) * 255)
                gv = math.cos(math.log(av) * (2 * math.pi / math.log(10)))
                gv = int((0.5 + 0.5 * gv) * 255)
                bv = (math.log(av - 1e-8) - math.log(1e-8)) / (
                    math.log(1e8) - math.log(1e-8)
                )
                bv = int(bv * 255)
                lv = math.sin(math.log(av) * (2 * math.pi / math.log(10)))
                lv = int((0.5 + 0.5 * lv) * 80)
            if color_type == "hsl":
                if negative:
                    color1 = f"hsl({lv + 180}, 100%, 50%)"
                else:
                    color1 = f"hsl({lv}, 100%, 50%)"
            else:
                color1 = f"rgb({rv}, {gv}, {bv})"
            g += f"""
              <rect x="{x}" y="{y1}" width="{width}" height="{height}" fill="{color1}" rx="0" ry="0" />
            """

        g += f"""
          <rect class="rect_g" x="{x}" y="{y - height * 11}" width="{width}" height="{height * 11}" fill="transparent" rx="2" ry="2" """
        if has_ref:
            g += f"""_has_ref="true" """
        for t in ("output", "grad"):
            for k in attributes[t]:
                g += f"""{t}_{k}="{attributes[t][k]}" """
        g += "/>"

        g += f"""
          <text text-anchor="" x="{x+width/2}" y="{y-height * 5}" font-size="14" font-family="{font_family}" fill="rgb(0,0,0)"></text>
          </g>
        """
        f.write(g)

        if len(children) == 0:
            continue

        offset = 0
        for i, child in enumerate(children):
            child_width = (
                node["node"][child]["length"] / total_length * (svg_width - 20)
            )
            child_node = {
                "x": x + offset,
                "y": y - height * 11,
                "width": child_width,
                "text": child,
                "node": node["node"][child],
            }
            offset += child_width
            bfs_queue.put(child_node)
    f.write("</svg>")
