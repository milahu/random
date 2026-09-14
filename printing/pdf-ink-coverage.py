#!/usr/bin/env python3

import re
import subprocess
import sys


def blackness(pdf_path):
    result = subprocess.run(
        [
            "gs",
            "-q",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-o", "-",
            "-sDEVICE=ink_cov",
            pdf_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )

    pattern = re.compile(
        r"^\s*"
        r"([0-9.]+)\s+"
        r"([0-9.]+)\s+"
        r"([0-9.]+)\s+"
        r"([0-9.]+)\s+"
        r"CMYK\s+OK\s*$"
    )

    k_values = []

    for line in result.stdout.splitlines():
        match = pattern.match(line)
        if match:
            k_values.append(float(match.group(4)))

    if not k_values:
        raise RuntimeError("No ink coverage data found")

    return sum(k_values) / len(k_values)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} FILE.pdf", file=sys.stderr)
        sys.exit(2)

    try:
        print(f"{blackness(sys.argv[1]):.2f}%")
    except subprocess.CalledProcessError as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
