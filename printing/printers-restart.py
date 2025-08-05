#!/usr/bin/env python3

# FIXME wake printers from "sleep" mode

# FIXME cups should try harder to connect to printers (retry more often?)

# ai promt at https://chat.deepseek.com/
r"""
create a python script that calls "LANG=C lpstat -p" and parses its output, for example

```
printer Brother_HL-L5100DN_1 now printing Brother_HL-L5100DN_1-294.  enabled since Di 05 Aug 2025 10:48:16 CEST
        Der Drucker kann nicht lokalisiert werden.
printer Brother_HL-L5100DN_10 now printing Brother_HL-L5100DN_10-299.  enabled since Di 05 Aug 2025 10:48:16 CEST
        Der Drucker kann nicht lokalisiert werden.
printer Brother_HL-L5100DN_11 now printing Brother_HL-L5100DN_11-300.  enabled since Di 05 Aug 2025 10:48:16 CEST
        Der Drucker kann nicht lokalisiert werden.
printer Brother_HL-L5100DN_12 now printing Brother_HL-L5100DN_12-301.  enabled since Di 05 Aug 2025 10:48:16 CEST
        Der Drucker kann nicht lokalisiert werden.
```

i need the printer names, for example

```
Brother_HL-L5100DN_1
Brother_HL-L5100DN_10
Brother_HL-L5100DN_11
Brother_HL-L5100DN_12
```

and i need the printer status, for example

```
Der Drucker kann nicht lokalisiert werden.
Der Drucker kann nicht lokalisiert werden.
Der Drucker kann nicht lokalisiert werden.
Der Drucker kann nicht lokalisiert werden.
```

if the status is "Der Drucker kann nicht lokalisiert werden."
then it should call, for example

```
cupsdisable Brother_HL-L5100DN_1
```

wait 1 second, and then call

```
cupsenable Brother_HL-L5100DN_1
```
"""

import os
import re
import time
import subprocess

def get_printer_status():
    # Run lpstat command and capture output
    result = subprocess.run(
        ['lpstat', '-p'],
        capture_output=True,
        text=True,
        env={
            "PATH": os.environ["PATH"],
            "LANG": "C",
        },
    )
    output = result.stdout.splitlines()

    printers = []
    current_printer = None

    for line in output:
        line = line.rstrip()
        # print("line", repr(line))
        if line.startswith('printer'):
            # Parse printer name
            parts = line.split()
            if len(parts) >= 2:
                current_printer = parts[1]
                # The status is everything after "enabled since..." or similar
                status_start = line.find('since') + 5
                # status = line[status_start:].strip()
                status = ""
                printers.append({'name': current_printer, 'status': status})
        elif line.startswith("\t") and current_printer:
            # This is a continuation line with additional status info
            # printers[-1]['status'] += ' ' + line
            printers[-1]['status'] = line.strip()

    return printers

def restart_printer(printer_name):
    print(f"  Restarting printer {printer_name}")
    subprocess.run(['cupsdisable', printer_name])
    # time.sleep(1) # not needed
    subprocess.run(['cupsenable', printer_name])

def main():
    printers = get_printer_status()

    target_status_regex_list = [
        re.compile(r"Der Drucker.* kann nicht lokalisiert werden\."),
        # TODO add more
    ]

    for printer in printers:

        if printer['status'] != "":
            print(f"Printer {printer['name']}: {printer['status']!r}")

        for target_status_regex in target_status_regex_list:
            if target_status_regex.fullmatch(printer['status']):
                restart_printer(printer['name'])
                break # stop regex loop

if __name__ == "__main__":
    main()
