#!/usr/bin/env python3

# https://stackoverflow.com/questions/9555118/parsing-string-with-kb-mb-gb-etc-into-numeric-value

import re;
parse_size = lambda s:(
    lambda m,e,i:float(m)*(1000+24*bool(i))**'1kmgtpezyrq'.find(e or "1")
)(*re.match(r'([0-9.]+)([kmgtpezyrq])?(i)?b?$',s.lower()).groups())

if __name__ == "__main__":
    # test
    sizes = [
      "100",
      "100B",
      "100KiB",
      "1.5KiB",
      "100MB",
      "1.5GB",
      "5i",
    ]
    for size in sizes:
        print(size, "=", parse_size(size))
