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
svg_height = 675
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
    .module_g:hover { stroke:black; stroke-width:0.5; cursor:pointer; }
    .color_g:hover {stroke:red; stroke-width:0.5; cursor:pointer; }
</style>
<script type="text/ecmascript">
<![CDATA[
    var details, svg;
    function init(evt) { 
        details = document.getElementById("details").firstChild; 
        searchbtn = document.getElementById("search");
        matchedtxt = document.getElementById("matched");
        svg = document.getElementsByTagName("svg")[0];
        searching = 0;
        unzoom();
    }

    // mouse-over for info
    function s(info) { details.nodeValue = "Module: " + info; }
    function c() { details.nodeValue = ' '; }

    // ctrl-F for search
    window.addEventListener("keydown",function (e) {
        if (e.keyCode === 114 || (e.ctrlKey && e.keyCode === 70)) { 
            e.preventDefault();
            search_prompt();
        }
    })

    // functions
    function find_child(parent, name, attr) {
        var children = parent.childNodes;
        for (var i=0; i<children.length;i++) {
            if (children[i].tagName == name)
                return (attr != undefined) ? children[i].attributes[attr].value : children[i];
        }
        return;
    }
    function orig_save(e, attr, val) {
        if (e.attributes["_orig_"+attr] != undefined) return;
        if (e.attributes[attr] == undefined) return;
        if (val == undefined) val = e.attributes[attr].value;
        e.setAttribute("_orig_"+attr, val);
    }
    function orig_load(e, attr) {
        if (e.attributes["_orig_"+attr] == undefined) return;
        e.attributes[attr].value = e.attributes["_orig_"+attr].value;
        e.removeAttribute("_orig_"+attr);
    }
    function g_to_text(e) {
        var text = find_child(e, "title").firstChild.nodeValue;
        return (text)
    }
    function g_to_func(e) {
        var func = g_to_text(e);
        if (func != null)
            func = func.replace(/ .*/, "");
        return (func);
    }
    function update_text(e) {
        var r = find_child(e, "rect");
        var t = find_child(e, "text");
        var w = parseFloat(r.attributes["width"].value) -3;
        var txt = find_child(e, "title").textContent.replace(/\([^(]*\)/,"");
        t.attributes["x"].value = parseFloat(r.attributes["x"].value) +3;

        // Smaller than this size won't fit anything
        if (w < 2*12*0.59) {
            t.textContent = "";
            return;
        }

        t.textContent = txt;
        // Fit in full text width
        if (/^ *$/.test(txt) || t.getSubStringLength(0, txt.length) < w)
            return;

        for (var x=txt.length-2; x>0; x--) {
            if (t.getSubStringLength(0, x+2) <= w) { 
                t.textContent = txt.substring(0,x) + "..";
                return;
            }
        }
        t.textContent = "";
    }

    // histogram
    function find_children(parent, name, attr) {
        var children = parent.childNodes;
        var child_nodes = [];
        for (var i=0; i<children.length;i++) {
            if (children[i].tagName == name) {
                if (children[i].attributes[attr] != undefined) {
                  child_nodes.push(children[i]);
                }
            }
        }
        return child_nodes;
    }

    function update_histogram_single(name, values) {
      var id_attr = "_his_";
      if (name.slice(-4) == "_ref") {
        name = name.slice(0, -4);
        id_attr = "_his_ref_";
      }
      var g_node = document.getElementById("his_"+name);
      var child_nodes = find_children(g_node, "rect", id_attr);
      for (var i = 0; i < child_nodes.length; ++i) {
        var child_node = child_nodes[i];
        var y = parseInt(child_node.attributes["y"].value);
        var height = parseInt(child_node.attributes["height"].value);
        y = y + height;
        var index = parseInt(child_node.attributes[id_attr].value);
        if (values.length == 0) {
            child_node.attributes["y"].value = y.toString();
            child_node.attributes["height"].value = "0";
            continue;
        }
        var value = parseFloat(values[index]);
        var min = parseFloat(values[0]);
        var max = parseFloat(values[10]);
        height = Math.round((value - min) / (max - min) * 100);
        height = height == 0 ? 1 : height;
        child_node.attributes["y"].value = (y - height).toString();
        child_node.attributes["height"].value = height.toString();
      }
    }

    function update_histogram(node) {
        var attr = find_child(node, "rect").attributes;
        const types = ["output", "grad"];
        const metrics = ["abs", "min", "max", "value", "positive", "rms", "stddev", "eigs"];
        for (var i = 0; i < types.length; ++i) {
          for (var j = 0; j < metrics.length; ++j) {
            var attr_name = types[i]+"_"+metrics[j];
            var values = [];
            if (attr[attr_name] != undefined) {
              values = attr[attr_name].value.split(" ");
            }
            update_histogram_single(attr_name, values);

            var attr_name = types[i]+"_"+metrics[j]+"_ref";
            var values = [];
            if (attr[attr_name] != undefined) {
              values = attr[attr_name].value.split(" ");
            }
            update_histogram_single(attr_name, values);
          }
        }
    }

    // zoom
    function zoom_reset(e) {
        if (e.attributes != undefined) {
            orig_load(e, "x");
            orig_load(e, "width");
        }
        if (e.childNodes == undefined) return;
        for(var i=0, c=e.childNodes; i<c.length; i++) {
            zoom_reset(c[i]);
        }
    }
    function zoom_child(e, x, ratio) {
        if (e.attributes != undefined) {
            if (e.attributes["x"] != undefined) {
                orig_save(e, "x");
                e.attributes["x"].value = (parseFloat(e.attributes["x"].value) - x - 10) * ratio + 10;
                if(e.tagName == "text") e.attributes["x"].value = find_child(e.parentNode, "rect", "x") + 3;
            }
            if (e.attributes["width"] != undefined) {
                orig_save(e, "width");
                e.attributes["width"].value = parseFloat(e.attributes["width"].value) * ratio;
            }
        }

        if (e.childNodes == undefined) return;
        for(var i=0, c=e.childNodes; i<c.length; i++) {
            zoom_child(c[i], x-10, ratio);
        }
    }
    function zoom_parent(e) {
        if (e.attributes) {
            if (e.attributes["x"] != undefined) {
                orig_save(e, "x");
                e.attributes["x"].value = 10;
            }
            if (e.attributes["width"] != undefined) {
                orig_save(e, "width");
                e.attributes["width"].value = parseInt(svg.width.baseVal.value) - (10*2);
            }
        }
        if (e.childNodes == undefined) return;
        for(var i=0, c=e.childNodes; i<c.length; i++) {
            zoom_parent(c[i]);
        }
    }
    function zoom(node) { 
        update_histogram(node);
        var attr = find_child(node, "rect").attributes;
        var width = parseFloat(attr["width"].value);
        var xmin = parseFloat(attr["x"].value);
        var xmax = parseFloat(xmin + width);
        var ymin = parseFloat(attr["y"].value);
        var ratio = (svg.width.baseVal.value - 2*10) / width;

        // XXX: Workaround for JavaScript float issues (fix me)
        var fudge = 0.000001;

        var unzoombtn = document.getElementById("unzoom");
        unzoombtn.style["opacity"] = "1.0";

        var el = document.getElementsByClassName("module_g");
        for(var i=0;i<el.length;i++){
            var e = el[i];
            var a = find_child(e, "rect").attributes;
            var ex = parseFloat(a["x"].value);
            var ew = parseFloat(a["width"].value);
            // Is it an ancestor
            if (0 == 0) {
                var upstack = parseFloat(a["y"].value) > ymin;
            } else {
                var upstack = parseFloat(a["y"].value) < ymin;
            }
            if (upstack) {
                // Direct ancestor
                if (ex <= xmin && (ex+ew+fudge) >= xmax) {
                    e.style["opacity"] = "0.5";
                    zoom_parent(e);
                    e.onclick = function(e){unzoom(); zoom(this);};
                    update_text(e);
                }
                // not in current path
                else
                    e.style["display"] = "none";
            }
            // Children maybe
            else {
                // no common path
                if (ex < xmin || ex + fudge >= xmax) {
                    e.style["display"] = "none";
                }
                else {
                    zoom_child(e, xmin, ratio);
                    e.onclick = function(e){zoom(this);};
                    update_text(e);
                }
            }
        }
    }
    function unzoom() {
        var unzoombtn = document.getElementById("unzoom");
        unzoombtn.style["opacity"] = "0.0";

        var el = document.getElementsByClassName("module_g");
        for(i=0;i<el.length;i++) {
            el[i].style["display"] = "block";
            el[i].style["opacity"] = "1";
            zoom_reset(el[i]);
            update_text(el[i]);
        }
    }

    // search
    function reset_search() {
        var el = document.getElementsByTagName("rect");
        for (var i=0; i < el.length; i++){
            orig_load(el[i], "fill")
        }
    }
    function search_prompt() {
        if (!searching) {
            var term = prompt("Enter a search term (regexp " +
                "allowed, eg: ^feedford)", "");
            if (term != null) {
                search(term)
            }
        } else {
            reset_search();
            searching = 0;
            searchbtn.style["opacity"] = "0.1";
            searchbtn.firstChild.nodeValue = "Search"
            matchedtxt.style["opacity"] = "0.0";
            matchedtxt.firstChild.nodeValue = ""
        }
    }
    function search(term) {
        var re = new RegExp(term);
        var el = document.getElementsByClassName("module_g");
        var matches = new Object();
        var maxwidth = 0;
        for (var i = 0; i < el.length; i++) {
            var e = el[i];
            if (e.attributes["class"].value != "module_g")
                continue;
            var func = g_to_func(e);
            var rect = find_child(e, "rect");
            if (rect == null) {
                // the rect might be wrapped in an anchor
                // if nameattr href is being used
                if (rect = find_child(e, "a")) {
                    rect = find_child(r, "rect");
                }
            }
            if (func == null || rect == null)
                continue;

            // Save max width. Only works as we have a root frame
            var w = parseFloat(rect.attributes["width"].value);
            if (w > maxwidth)
                maxwidth = w;

            if (func.match(re)) {
                // highlight
                var x = parseFloat(rect.attributes["x"].value);
                orig_save(rect, "fill");
                rect.attributes["fill"].value =
                    "rgb(230,0,230)";

                // remember matches
                if (matches[x] == undefined) {
                    matches[x] = w;
                } else {
                    if (w > matches[x]) {
                        // overwrite with parent
                        matches[x] = w;
                    }
                }
                searching = 1;
            }
        }
        if (!searching)
            return;

        searchbtn.style["opacity"] = "1.0";
        searchbtn.firstChild.nodeValue = "Reset Search"

        // calculate percent matched, excluding vertical overlap
        var count = 0;
        var lastx = -1;
        var lastw = 0;
        var keys = Array();
        for (k in matches) {
            if (matches.hasOwnProperty(k))
                keys.push(k);
        }
        // sort the matched frames by their x location
        // ascending, then width descending
        keys.sort(function(a, b){
                return a - b;
            if (a < b || a > b)
                return a - b;
            return matches[b] - matches[a];
        });
        // Step through frames saving only the biggest bottom-up frames
        // thanks to the sort order. This relies on the tree property
        // where children are always smaller than their parents.
        for (var k in keys) {
            var x = parseFloat(keys[k]);
            var w = matches[keys[k]];
            if (x >= lastx + lastw) {
                count += w;
                lastx = x;
                lastw = w;
            }
        }
        // display matched percent
        matchedtxt.style["opacity"] = "1.0";
        pct = 100 * count / maxwidth;
        if (pct == 100)
            pct = "100"
        else
            pct = pct.toFixed(1)
        matchedtxt.firstChild.nodeValue = "Matched: " + pct + "%";
    }
    function searchover(e) {
        searchbtn.style["opacity"] = "1.0";
    }
    function searchout(e) {
        if (searching) {
            searchbtn.style["opacity"] = "1.0";
        } else {
            searchbtn.style["opacity"] = "0.1";
        }
    }

    // color scheme
    function update_color(item) {
       var current_color_node = document.getElementById("current_color");
       var current_color = current_color_node.textContent.split(" ");
       if (item == "output" || item == "grad") {
         current_color[0] = item;
       } else if (item == "mean" || item == "rms" || item == "norm") {
         current_color[1] = item;
       } else {
         current_color[2] = item;
       }
       const items = ["output", "grad", "mean", "norm", "rms", "value", "abs", "max", "min", "positive", "rmsp", "stddev", "eigs"];
       var objs = {};
       for (var i=0; i < items.length; ++i) {
         objs[items[i]] = document.getElementById("color_"+items[i]);
         if (current_color.indexOf(items[i]) != -1) {
           objs[items[i]].style["opacity"] = "1.0";
           objs[items[i]].style["fill"] = "red";
         } else {
           objs[items[i]].style["opacity"] = "0.5";
           objs[items[i]].style["fill"] = "black";
         }
       }
       current_color_node.textContent = current_color.join(" ");
       update_node_color(current_color);
    }
    function update_node_color(color) {
      var el = document.getElementsByClassName("module_g");
      for(i=0;i<el.length;i++) {
        var rect_node = find_child(el[i], "rect");
        var attr_name = color[0] + "_" + color[2];
        var has_ref = true;
        if (rect_node.attributes["_has_ref"] == undefined) {
            has_ref = false;
        }
        if (rect_node.attributes[attr_name] == undefined) {
          if (has_ref) {
              rect_node.style["fill"] = "rgb(255, 255, 255)";
          } else {
              rect_node.style["fill"] = "rgb(255, 240, 0)";
          }
          continue;
        }
        var value = rect_node.attributes[attr_name].value.split(" ");
        var ref_value = undefined;
        if (has_ref) {
          ref_value = rect_node.attributes[attr_name+"_ref"].value.split(" ");
        }
        console.log(has_ref, value, ref_value);
        var metric = "";
        if (color[1] == "mean") {
          metric = parseFloat(value[11]);
        } else if (color[1] == "rms") {
          metric = parseFloat(value[12]);
        } else {
          if (value.length == 15) {
            metric = parseFloat(value[14]);
          }
        }
        var ref_metric = "";
        if (has_ref) {
          if (color[1] == "mean") {
            ref_metric = parseFloat(ref_value[11]);
          } else if (color[1] == "rms") {
            ref_metric = parseFloat(ref_value[12]);
          } else {
            if (ref_value.length == 15) {
              ref_metric = parseFloat(ref_value[14]);
            }
          }
        }
        console.log(has_ref, metric, ref_metric);
        if (metric == "") {
          if (has_ref) {
              rect_node.style["fill"] = "rgb(255, 255, 255)";
          } else {
              rect_node.style["fill"] = "rgb(255, 240, 0)";
          }
        } else {
          if (has_ref) {
             var diff = metric - ref_metric;
             if (diff > 0) {
               rect_node.style["fill"] = "rgb(255,0,0)";
             } else if (diff < 0) {
               rect_node.style["fill"] = "rgb(0,0,255)";
             } else {
               rect_node.style["fill"] = "rgb(255,255,255)";
             }
          } else {
              var color_g = Math.round((1 - metric) * 255);
              color_g = color_g < 0 ? 0 : color_g;
              color_g = color_g > 225 ? 225 : color_g;
              rect_node.style["fill"] = "rgb(255," + color_g + ",0)";
          }
        }
      }
    }
]]>
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
<text text-anchor="" x="268" y="100" font-size="12" font-family="{font_family}" font-weight="bold" fill="rgb(0,0,0)" >|</text>
<text class="color_g" style="opacity: 1.0" onclick="update_color('mean')" id="color_mean" text-anchor="" x="280" y="100" font-size="12" font-family="{font_family}" fill="red" >mean</text>
<text class="color_g" style="opacity: 0.5" onclick="update_color('rms')" id="color_rms" text-anchor="" x="324" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >rms</text>
<text class="color_g" style="opacity: 0.5" onclick="update_color('norm')" id="color_norm" text-anchor="" x="358" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >norm</text>
<text text-anchor="" x="398" y="100" font-size="12" font-family="{font_family}" font-weight="bold" fill="rgb(0,0,0)" >|</text>
<text class="color_g" style="opacity: 0.5" onclick="update_color('value')" id="color_value" text-anchor="" x="411" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >value</text>
<text class="color_g" style="opacity: 1.0" onclick="update_color('abs')" id="color_abs" text-anchor="" x="451" y="100" font-size="12" font-family="{font_family}" fill="red" >abs</text>
<text class="color_g" style="opacity: 0.5" onclick="update_color('max')" id="color_max" text-anchor="" x="483" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >max</text>
<text class="color_g" style="opacity: 0.5" onclick="update_color('min')" id="color_min" text-anchor="" x="515" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >min</text>
<text class="color_g" style="opacity: 0.5" onclick="update_color('positive')" id="color_positive" text-anchor="" x="547" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >positive</text>
<text class="color_g" style="opacity: 0.5" onclick="update_color('rmsp')" id="color_rmsp" text-anchor="" x="605" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >rms</text>
<text class="color_g" style="opacity: 0.5" onclick="update_color('stddev')" id="color_stddev" text-anchor="" x="640" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >stddev</text>
<text class="color_g" style="opacity: 0.5" onclick="update_color('eigs')" id="color_eigs" text-anchor="" x="690" y="100" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >eigs</text>

<text text-anchor="" x="{svg_width - 120}" y="24" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" id="search" onmouseover="searchover()" onmouseout="searchout()" onclick="search_prompt()" style="opacity:0.1;cursor:pointer" >Search</text>
<text text-anchor="" x="{svg_width-120}" y="{svg_height-15}" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" id="matched" > </text>
<text text-anchor="" x="10.00" y="{svg_height-15}" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" id="details" > </text>

<text text-anchor="" x="10.00" y="200" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >Percentiles</text>
<text text-anchor="" x="10.00" y="213" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >(Output/Weight)</text>
<text text-anchor="" x="10.00" y="330" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >Percentiles</text>
<text text-anchor="" x="10.00" y="343" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)" >(Gradient)</text>
"""

start_x = 150
start_y = 150
metrics = ["abs", "min", "max", "value", "positive", "rms", "stddev", "eigs"]
for i, m in enumerate(metrics):
    x = start_x + i * 220
    y = start_y
    svg_head += f"""
    <g id="his_output_{m}">
    <rect x="{x}" y="{y}" width="165" height="100" rx="0" ry="0" fill="transparent" style="stroke:black;stroke-width:0.1" />
    """
    for j in range(11):
        if has_ref:
            xx = x + 5 + j * 14 + 2
            yy = y + 100
            svg_head += f"""<rect _his_="{j}" x="{xx}" y="{yy}" width="2" height="0" rx="0" ry="0" fill="lightblue" />"""
            svg_head += f"""<rect _his_ref_="{j}" x="{xx+6}" y="{yy}" width="2" height="0" rx="0" ry="0" fill="red" />"""
        else:
            xx = x + 5 + j * 14 + 4
            yy = y + 100
            svg_head += f"""<rect _his_="{j}" x="{xx}" y="{yy}" width="6" height="0" rx="0" ry="0" fill="lightblue" />"""

    svg_head += f"""
    <text text-anchor="middle" x="{x + 75}" y="{y + 120}" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)">{m}</text>
    </g>
    """
    y = start_y + 130
    svg_head += f"""
    <g id="his_grad_{m}">
    <rect x="{x}" y="{y}" width="165" height="100" rx="0" ry="0" fill="transparent" style="stroke:black;stroke-width:0.1" />
    """
    for j in range(11):
        if has_ref:
            xx = x + 5 + j * 14 + 2
            yy = y + 100
            svg_head += f"""<rect _his_="{j}" x="{xx}" y="{yy}" width="2" height="0" rx="0" ry="0" fill="lightblue" />"""
            svg_head += f"""<rect _his_ref_="{j}" x="{xx+6}" y="{yy}" width="2" height="0" rx="0" ry="0" fill="red" />"""
        else:
            xx = x + 5 + j * 14 + 4
            yy = y + 100
            svg_head += f"""<rect _his_="{j}" x="{xx}" y="{yy}" width="6" height="0" rx="0" ry="0" fill="lightblue" />"""
    svg_head += f"""
    <text text-anchor="middle" x="{x + 75}" y="{y + 120}" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)">{m}</text>
    </g>
    """

bfs_node = {
    "x": 10,
    "y": svg_height - 50,
    "width": svg_width - 20,
    "text": "root",
    "node": tree,
}
bfs_queue = queue.Queue()
bfs_queue.put(bfs_node)
total_length = tree["length"]
default_scheme = {"type": "output", "attr": "abs", "metric": "mean"}

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

        # get value and fill color
        color_r = 255
        color_g = 255 if has_ref else 240
        color_b = 255 if has_ref else 0
        attributes = {"output": {}, "grad": {}}
        module_type = None
        if "output" in keys or "param_value" in keys:
            assert ("output" in keys and "param_value" not in keys) or (
                "output" not in keys and "param_value" in keys
            ), keys

            for k in ("output", "grad", "param_value", "param_grad"):
                if k not in keys:
                    continue
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

                            if (
                                default_scheme["type"] == k
                                and default_scheme["attr"] == attr
                            ):
                                if "type" in item:
                                    module_type = item["type"]
                                if has_ref:
                                    ref_metric = f"{default_scheme['metric']}_ref"
                                    metric = default_scheme["metric"]
                                    if ref_metric in item:
                                        diff = float(item[metric]) - float(
                                            item[ref_metric]
                                        )
                                        if diff > 0:
                                            color_g = 0
                                            color_b = 0
                                        elif diff == 0:
                                            color_g = 255
                                            color_b = 255
                                        else:
                                            color_r = 0
                                            color_g = 0
                                            color_b = 255
                                    else:
                                        color_r, color_g, color_b = (255, 255, 255)
                                else:
                                    color_g = (
                                        1 - float(item[default_scheme["metric"]])
                                    ) * 255
                                    color_g = 0 if color_g < 0 else int(color_g)
                                    color_g = 225 if color_g > 225 else int(color_g)

        x, y, width, text = node["x"], node["y"], node["width"], node["text"]
        text = text if module_type is None else text + f" ({module_type})"
        g = f"""
          <g class="module_g" onmouseover="s('{text}')" onmouseout="c()" onclick="zoom(this)">
          <title>{text}</title><rect x="{x}" y="{y}" width="{width}" height="15.0" fill="rgb({color_r},{color_g},{color_b})" rx="2" ry="2" """
        if has_ref:
            g += f"""_has_ref="true" """
        for t in ("output", "grad"):
            for k in attributes[t]:
                g += f"""{t}_{k}="{attributes[t][k]}" """
        g += f"""/>
          <text text-anchor="" x="{x+3}" y="{y+10.5}" font-size="12" font-family="{font_family}" fill="rgb(0,0,0)"></text>
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
                "y": y - 15,
                "width": child_width,
                "text": child,
                "node": node["node"][child],
            }
            offset += child_width
            bfs_queue.put(child_node)
    f.write("</svg>")
