#!/usr/bin/env python3

# https://stackoverflow.com/questions/13927889
# Show non printable characters in a string



# hex-escape all non-ascii chars in a bytestring

import string, random

def hex_escape(bs):
    "hex-escape all non-ascii chars in a bytestring"
    assert isinstance(bs, bytes)
    #p = string.printable # also contains "\n"
    p = string.ascii_letters + string.digits + string.punctuation + " "
    p = p.encode("ascii")
    return "".join([(chr(b) if b in p else f"\\x{b:02x}") for b in bs])

print(hex_escape(random.randbytes(10)))



# or with regex

import re, string, random

def hex_escape(bs):
    "hex-escape all non-ascii chars in a bytestring"
    assert isinstance(bs, bytes)
    #p = string.printable # also contains "\n"
    p = string.ascii_letters + string.digits + string.punctuation + " "
    r = ("([^" + re.escape(p) + "])").encode("ascii")
    x = re.compile(r)
    def escape(m):
        return r"\x{0:02x}".format(m.group(0)[0]).encode("ascii")
    return x.sub(escape, bs).decode("ascii")

print(hex_escape(random.randbytes(10)))
