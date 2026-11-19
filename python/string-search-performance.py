#!/usr/bin/env python3

# results:
r'''
A0 0.100
B1 0.049
B2 1.200
C0 0.067
'''

# NOTE performance depends on the input data
# in this case the lists "strings" and "bytestrings"
# so as always:
# do your own benchmarks with your input data

import re, random, timeit

randbytes = random.randbytes(1_000_000)

# construct a bad case for version B2
randbytes_bad = (
    b"b" +
    randbytes.replace(b"a", b"_").replace(b"b", b"_") +
    b"a"
)

format = "%.3f"

# request:
# check whether the bytestring randbytes contains the bytes b"a" or b"b"

print("A0", format % timeit.timeit(lambda: re.search(b"a|b", randbytes), number=100_000))

print("B1", format % timeit.timeit(lambda: any(c in randbytes for c in (b"a", b"b")), number=100_000))

print("B2", format % timeit.timeit(lambda: any(c in randbytes_bad for c in (b"a", b"b")), number=100_000))

regex = re.compile(b"a|b")
print("C0", format % timeit.timeit(lambda: regex.search(randbytes), number=100_000))
