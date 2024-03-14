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
window.addEventListener("keydown", function(e) {
  if (e.keyCode === 114 || (e.ctrlKey && e.keyCode === 70)) {
    e.preventDefault();
    search_prompt();
  }
})

// functions
function find_child(parent, name, attr) {
  var children = parent.childNodes;
  for (var i = 0; i < children.length; i++) {
    if (children[i].tagName == name)
      return (attr != undefined) ? children[i].attributes[attr].value
                                 : children[i];
  }
  return;
}
function orig_save(e, attr, val) {
  if (e.attributes["_orig_" + attr] != undefined)
    return;
  if (e.attributes[attr] == undefined)
    return;
  if (val == undefined)
    val = e.attributes[attr].value;
  e.setAttribute("_orig_" + attr, val);
}
function orig_load(e, attr) {
  if (e.attributes["_orig_" + attr] == undefined)
    return;
  e.attributes[attr].value = e.attributes["_orig_" + attr].value;
  e.removeAttribute("_orig_" + attr);
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
  var w = parseFloat(r.attributes["width"].value) - 3;
  // var txt = find_child(e, "title").textContent.replace(/\([^(]*\)/, "");
  var txt = find_child(e, "title").textContent
  if (txt != "") {
    txt = txt.split(" ")[0].split(".");
    if (txt.length == 1) {
      txt = txt[0];
    } else {
      txt = txt[txt.length - 2];
    }
  }
  t.attributes["x"].value = parseFloat(r.attributes["x"].value) + 3;

  // Smaller than this size won't fit anything
  if (w < 2 * 14 * 0.59) {
    t.textContent = "";
    return;
  }

  t.textContent = txt;
  // Fit in full text width
  if (/^ *$/.test(txt) || t.getSubStringLength(0, txt.length) < w)
    return;

  for (var x = txt.length - 2; x > 0; x--) {
    if (t.getSubStringLength(0, x + 2) <= w) {
      t.textContent = txt.substring(0, x) + "..";
      return;
    }
  }
  t.textContent = "";
}

// histogram
function find_children(parent, name, attr) {
  var children = parent.childNodes;
  var child_nodes = [];
  for (var i = 0; i < children.length; i++) {
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
  var g_node = document.getElementById("his_" + name);
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
  const types = [ "output", "grad" ];
  const metrics =
      [ "abs", "min", "max", "value", "positive", "rms", "stddev", "eigs" ];
  for (var i = 0; i < types.length; ++i) {
    for (var j = 0; j < metrics.length; ++j) {
      var attr_name = types[i] + "_" + metrics[j];
      var values = [];
      if (attr[attr_name] != undefined) {
        values = attr[attr_name].value.split(" ");
      }
      update_histogram_single(attr_name, values);

      var attr_name = types[i] + "_" + metrics[j] + "_ref";
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
  if (e.childNodes == undefined)
    return;
  for (var i = 0, c = e.childNodes; i < c.length; i++) {
    zoom_reset(c[i]);
  }
}

function zoom_child(e, x, ratio) {
  if (e.attributes != undefined) {
    if (e.attributes["x"] != undefined) {
      orig_save(e, "x");
      e.attributes["x"].value =
          (parseFloat(e.attributes["x"].value) - x - 10) * ratio + 10;
      if (e.tagName == "text")
        e.attributes["x"].value = find_child(e.parentNode, "rect", "x") + 3;
    }
    if (e.attributes["width"] != undefined) {
      orig_save(e, "width");
      e.attributes["width"].value =
          parseFloat(e.attributes["width"].value) * ratio;
    }
  }

  if (e.childNodes == undefined)
    return;
  for (var i = 0, c = e.childNodes; i < c.length; i++) {
    zoom_child(c[i], x - 10, ratio);
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
      e.attributes["width"].value =
          parseInt(svg.width.baseVal.value) - (10 * 2);
    }
  }
  if (e.childNodes == undefined)
    return;
  for (var i = 0, c = e.childNodes; i < c.length; i++) {
    zoom_parent(c[i]);
  }
}

function zoom(node) {
  // update_histogram(node);
  var attr = find_child(node, "rect").attributes;
  var width = parseFloat(attr["width"].value);
  var xmin = parseFloat(attr["x"].value);
  var xmax = parseFloat(xmin + width);
  var ymin = parseFloat(attr["y"].value);
  var ratio = (svg.width.baseVal.value - 2 * 10) / width;

  // XXX: Workaround for JavaScript float issues (fix me)
  var fudge = 0.000001;

  var unzoombtn = document.getElementById("unzoom");
  unzoombtn.style["opacity"] = "1.0";

  var el = document.getElementsByClassName("module_g");
  for (var i = 0; i < el.length; i++) {
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
      if (ex <= xmin && (ex + ew + fudge) >= xmax) {
        e.style["opacity"] = "0.5";
        zoom_parent(e);
        e.onclick = function(e) {
          unzoom();
          zoom(this);
        };
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
      } else {
        zoom_child(e, xmin, ratio);
        e.onclick = function(e) { zoom(this); };
        update_text(e);
      }
    }
  }
}
function unzoom() {
  var unzoombtn = document.getElementById("unzoom");
  unzoombtn.style["opacity"] = "0.0";

  var el = document.getElementsByClassName("module_g");
  for (i = 0; i < el.length; i++) {
    el[i].style["display"] = "block";
    el[i].style["opacity"] = "1";
    zoom_reset(el[i]);
    update_text(el[i]);
  }
}

// search
function reset_search() {
  var el = document.getElementsByTagName("rect");
  for (var i = 0; i < el.length; i++) {
    orig_load(el[i], "fill")
  }
}
function search_prompt() {
  if (!searching) {
    var term = prompt("Enter a search term (regexp " +
                          "allowed, eg: ^feedford)",
                      "");
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
      rect.attributes["fill"].value = "rgb(230,0,230)";

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
  keys.sort(function(a, b) {
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
    else pct = pct.toFixed(1)
    matchedtxt.firstChild.nodeValue = "Matched: " + pct + "%";
}
function searchover(e) { searchbtn.style["opacity"] = "1.0"; }
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
  const items = [
    "output", "grad", "mean", "norm", "rms", "value", "abs", "max", "min",
    "positive", "rmsp", "stddev", "eigs"
  ];
  var objs = {};
  for (var i = 0; i < items.length; ++i) {
    objs[items[i]] = document.getElementById("color_" + items[i]);
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
  for (i = 0; i < el.length; i++) {
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
      ref_value = rect_node.attributes[attr_name + "_ref"].value.split(" ");
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
