import re
import sys
import json
import queue
import math

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

# extract diagnostics info
matched_lines = []
with open(sys.argv[1], "r") as f:
    for line in f:
        match = None
        for p in patterns:
            match = p.match(line.strip())
            if match is not None:
                matched_lines.append(match.groupdict())
                break

# built structure
tree = {}
for line in matched_lines:
    module = line["module"]
    print(module)
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


def get_width(node):
    if isinstance(node, list):
        return 1
    current = 0
    if "output" in node.keys():
        current = get_width(node["output"]) * 2
    child = 0
    for key in node.keys():
        if key in ("output", "grad", "output[0]"):
            continue
        child += get_width(node[key])
    node["length"] = max(current, child)
    return node["length"]


get_width(tree)

print(json.dumps(tree, indent=2))

svg_width = 1900
svg_height = 626
svg_title = "Diagnostics"

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
	.func_g:hover { stroke:black; stroke-width:0.5; cursor:pointer; }
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
		
		var el = document.getElementsByTagName("g");
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
		
		var el = document.getElementsByTagName("g");
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
		var el = document.getElementsByTagName("g");
		var matches = new Object();
		var maxwidth = 0;
		for (var i = 0; i < el.length; i++) {
			var e = el[i];
			if (e.attributes["class"].value != "func_g")
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
]]>
</script>
"""

svg_head += f"""
<rect x="0.0" y="0" width="{svg_width}" height="{svg_height}" fill="url(#background)"  />
<text text-anchor="middle" x="{svg_width / 2}" y="24" font-size="17" font-family="Verdana" fill="rgb(0,0,0)">{svg_title}</text>
<text text-anchor="" x="10.00" y="{svg_height-15}" font-size="12" font-family="Verdana" fill="rgb(0,0,0)" id="details" > </text>
<text text-anchor="" x="10.00" y="24" font-size="12" font-family="Verdana" fill="rgb(0,0,0)" id="unzoom" onclick="unzoom()" style="opacity:0.0;cursor:pointer" >Reset Zoom</text>
<text text-anchor="" x="{svg_width - 120}" y="24" font-size="12" font-family="Verdana" fill="rgb(0,0,0)" id="search" onmouseover="searchover()" onmouseout="searchout()" onclick="search_prompt()" style="opacity:0.1;cursor:pointer" >Search</text>
<text text-anchor="" x="{svg_width-120}" y="{svg_height-15}" font-size="12" font-family="Verdana" fill="rgb(0,0,0)" id="matched" > </text>
"""


example = """
<g class="func_g" onmouseover="s('all (2,963 samples, 100%)')" onmouseout="c()" onclick="zoom(this)">
<title>all (2,963 samples, 100%)</title><rect x="10.0" y="577" width="1180.0" height="15.0" fill="rgb(238,122,34)" rx="2" ry="2" />
<text text-anchor="" x="13.00" y="587.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"></text>
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
        color = 200
        if "output" in keys:
            for item in node["node"]["output"]:
                if "abs" in item:
                    color = (1 - float(item["mean"])) * 255
                    color = 0 if color < 0 else int(color)
                    color = 200 if color > 200 else int(color)
                    break

        if "param_value" in keys:
            for item in node["node"]["param_value"]:
                if "abs" in item:
                    color = (1 - float(item["mean"])) * 255
                    color = 0 if color < 0 else int(color)
                    color = 200 if color > 200 else int(color)
                    break

        x, y, width, text = node["x"], node["y"], node["width"], node["text"]

        vtext = text[0 : math.floor(width / (2 * 12 * 0.59))]
        g = f"""
          <g class="func_g" onmouseover="s('{text}')" onmouseout="c()" onclick="zoom(this)">
          <title>{text}</title><rect x="{x}" y="{y}" width="{width}" height="15.0" fill="rgb(255,{color},{color})" rx="2" ry="2" />
          <text text-anchor="" x="{x+3}" y="{y+10.5}" font-size="12" font-family="Verdana" fill="rgb(0,0,0)">{vtext}</text>
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
