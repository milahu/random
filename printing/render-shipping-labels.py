#!/usr/bin/env python3

sender_address = ", ".join([
  "Milan Hauth",
  "Jägerstr 10",
  "D-83308 Trostberg",
  # "83308 Trostberg", "Deutschland",
])

import sys

input_file = sys.argv[1]

# 105 * 2 = 210
# 57 * 5 = 285
# (297 - 285) / 2 = 6

num_labels_per_page_width = 2
num_labels_per_page_height = 5

output_html = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    @page {
      size: A4;
      margin: 0;
    }
    html, body, pre, div {
        margin: 0;
        padding: 0;
    }
    .label {
        font-family: sans-serif;
        font-size: 12pt;
    }
    .label > .from {
        border-bottom: solid 1px black;
        padding-bottom: 0.25em;
        margin-bottom: 1em;
    }
    .label > .to {
        line-height: 125%;
    }
    :root {
      --page-width: 210mm;
      /* actually 297mm but chrome says no
      --page-height: 297mm;
      */
      --page-height: 298mm;
      --label-width: 105mm;
      --label-height: 57mm;
      --num-labels-per-page-width: """ + str(num_labels_per_page_width) + """;
      --num-labels-per-page-height: """ + str(num_labels_per_page_height) + """;
      --page-padding-y: calc((var(--page-height) - (var(--num-labels-per-page-height) * var(--label-height))) / 2);
    }
    .page {
      width: var(--page-width);
      height: var(--page-height);
      /* fixme disable padding collapse */
      /* padding: var(--page-padding-y) 0; */
    }
    table {
        border-collapse: collapse;
        border: none;
    }
    .label {
      width: var(--label-width);
      height: var(--label-height);
      padding: 1em;
      box-sizing: border-box;
      -webkit-border-horizontal-spacing: 0;
      -webkit-border-vertical-spacing: 0;
    }
    .page-height-spacer {
      height: var(--page-padding-y);
    }
    @media screen {
      .page {
        outline: dotted 1px red;
      }
      .label:hover {
        background: gray;
      }
      .page-height-spacer:hover {
        background: green;
      }
    }
  </style>
</head>
<body>
"""

num_labels_per_page_width = 2
num_labels_per_page_height = 5

next_label_x = 0
next_label_y = 0

def render_address(lines):
    assert len(lines) <= 7, f"too many lines: {lines}"
    global next_label_x
    global next_label_y
    if not lines:
        return ""
    res = ""
    res += f"\n<!-- label x={next_label_x} y={next_label_y} -->\n"
    if next_label_x == 0 and next_label_y == 0:
        res += "<div class=page>"
        res += "<div class=page-height-spacer></div>"
        res += "<table>"
    if next_label_x == 0:
        res += "<tr>"
    res += "<td>"
    res += "<div class=label>\n"
    res += "<div class=from>"
    res += sender_address
    res += "</div>\n"
    res += "<div class=to>"
    for line in lines:
        res += line + "<br>"
    res = res.rstrip()
    res += "</div>\n"
    res += "</div>\n"
    res += "</td>"
    if next_label_x == num_labels_per_page_width - 1:
        res += "</tr>"
        next_label_x = 0
        next_label_y += 1
    else:
        next_label_x += 1
    if next_label_y == num_labels_per_page_height:
        res += "</table>"
        res += "<div class=page-height-spacer></div>"
        res += "</div>"
        res += "\n"
        next_label_y = 0
    return res

body_lines = []

with open(input_file) as f:
    for line in f.readlines():
        line = line.rstrip() # remove "\n"
        if line == "":
            continue
        # print(f"line[0]: {line[0]!r}")
        if line[0] in (" ", "\t"):
            # body line
            line = line.strip() # remove indent
            body_lines.append(line)
        else:
            # head line
            # print(f"head: {line!r}")
            output_html += "\n<!-- " + line + "-->\n"
            # TODO finish last body, start new body
            output_html += render_address(body_lines)
            body_lines = []

output_html += render_address(body_lines)

print(output_html)
