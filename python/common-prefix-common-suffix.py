#!/usr/bin/env python3

# common prefix and common suffix of a list of strings
# https://stackoverflow.com/a/6719272/10440128
# https://codereview.stackexchange.com/a/145762/205605

import itertools

def all_equal(it):
    x0 = it[0]
    return all(x0 == x for x in it)

def common_prefix(strings):
    char_tuples = zip(*strings)
    prefix_tuples = itertools.takewhile(all_equal, char_tuples)
    return "".join(x[0] for x in prefix_tuples)

def common_suffix(strings):
    return common_prefix(map(reversed, strings))[::-1]

strings = ["aa1zz", "aaa2zzz", "aaaa3zzzz"]

assert common_prefix(strings) == "aa"
assert common_suffix(strings) == "zz"

print("ok")
