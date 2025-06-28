#!/usr/bin/env python3

# https://nixos.wiki/wiki/Printing#Adding_printers

# see cups error log:
# journalctl -u cups.service | grep -F "[cups-driverd] Unable to open"
ppd_of_model = {
  "Brother HL-L5100DN for CUPS": "brother-HLL5100DN-cups-en.ppd",
}

import sys
import re

printers_conf_path = sys.argv[1]

with open(printers_conf_path) as f:
  printers_conf_text = f.read()

res = [
  "  # Enable CUPS to print documents.",
  "  services.printing.enable = true;",
  "",
  "  # add printers",
  "  # https://nixos.wiki/wiki/Printing#Adding_printers",
  "  hardware.printers = {",
  "    ensurePrinters = [",
]

regex_printer = r"<Printer ([^>]+)>\n(.*?)\n</Printer>"

for match in re.finditer(regex_printer, printers_conf_text, re.S):
  # https://stackoverflow.com/questions/2827623/how-can-i-create-an-object-and-add-attributes-to-it
  printer = lambda: None
  printer.name = match.group(1)
  # printer.somefield = 'somevalue'
  for line in match.group(2).split("\n"):
    # print(f"line {line!r}")
    parts = line.strip().split(" ", 1)
    key = parts[0]
    try:
      val = parts[1]
    except IndexError:
      val = ""
    setattr(printer, key, val)
  ppd = ppd_of_model.get(printer.MakeModel)
  if not ppd:
    ppd = f"todo-find-ppd-file-for-printer-{printer.name}.ppd"
  res += [
    '      {',
    f'        name = "{printer.name}";',
    f'        location = "{printer.Location}";',
    f'        deviceUri = "{printer.DeviceURI}";',
    f'        model = "{printer.name}.ppd";',
    '        ppdOptions = {',
    f'          PageSize = "A4";',
    '        };',
    '      }',
  ]

res += [
  "    ];",
  "  };",
]

print("".join(map(lambda s: s + "\n", res)))
