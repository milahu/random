#!/usr/bin/env python3

# Python string join performance
# https://stackoverflow.com/questions/476772/python-string-join-performance

# NOTE performance depends on the input data
# in this case the lists "strings" and "bytestrings"
# so as always:
# do your own benchmarks with your input data

# NOTE for the special case of joining many identical strings
# you should use the string multiplication operator.
# example: join many placeholders for a SQL query:
# placeholders = (len(values) * "?,")[:-1]
r'''
>>> import timeit; timeit.timeit(lambda: (10_000 * "?,")[:-1], number=10_000)
0.009677325142547488

>>> import timeit; timeit.timeit(lambda: (10_000 * ",?")[1:], number=10_000)
0.009842365980148315

>>> import timeit; timeit.timeit(lambda: ",".join(["?"] * 10_000), number=10_000)
0.640322616090998

>>> import timeit; timeit.timeit(lambda: ",".join("?" * 10_000), number=10_000)
0.8513069730252028

>>> import timeit; timeit.timeit(lambda: ",".join("?" for _ in range(10_000)), number=10_000)
3.806926750112325
'''

# results:
# CPU: AMD Ryzen 5 5600H, 6C/12T, 3.30-4.20GHz
r'''
0.040 join
0.064 join_bytestrings
0.196 copy_and_join
0.224 copy_and_join_bytestrings
0.304 stringio
0.316 bytearray
0.332 concat
3.642 concat_bytestring
'''

# based on:
# Source - https://stackoverflow.com/a/65019934
# Posted by Paolo Bonzini
# Retrieved 2026-11-16, License - CC BY-SA 4.0

from io import StringIO
from array import array

loop_count = 10000
strings = [str(num) for num in range(loop_count)]
bytestrings = [b'%d' % num for num in range(loop_count)]

# 1.1453419709578156 seconds for 1000 repetitions (fastest of 5)
def concat():
  out = ''
  for s in strings:
    out += s
  return out

def concat_bytestring():
  out = b''
  for s in bytestrings:
    out += s
  return out

# 1.468063525040634 seconds for 1000 repetitions
# Removing decode() does not make it faster
def bytearray():
  out = array('b')
  for b in bytestrings:
    out.frombytes(b)
  return out.tobytes().decode()

# 0.9110414159949869 seconds for 1000 repetitions
def copy_and_join():
  # I am rebuilding the list on purpose: I don't want to include
  # the overhead of printing numbers, but I do want to include
  # the overhead of building the list
  str_list = []
  for s in strings:
    str_list.append(s)
  return ''.join(str_list)

def copy_and_join_bytestrings():
  # I am rebuilding the list on purpose: I don't want to include
  # the overhead of printing numbers, but I do want to include
  # the overhead of building the list
  str_list = []
  for s in bytestrings:
    str_list.append(s)
  return b''.join(str_list)

def join():
  return ''.join(strings)

def join_bytestrings():
  return b''.join(bytestrings)

# 1.174764319031965 seconds for 1000 repetitions
def stringio():
  io = StringIO()
  for s in strings:
    io.write(s)
  return io.getvalue()



import timeit

format = "%5.3f %s"
# format = "%6.4f %s"

for round_idx in range(3):
    print()
    print(f"round {round_idx + 1}")
    r'''
    print(format % (timeit.timeit(concat, number=1000), "concat"))
    print(format % (timeit.timeit(concat_bytestring, number=1000), "concat_bytestring"))
    print(format % (timeit.timeit(bytearray, number=1000), "bytearray"))
    print(format % (timeit.timeit(copy_and_join, number=1000), "copy_and_join"))
    print(format % (timeit.timeit(copy_and_join_bytestrings, number=1000), "copy_and_join_bytestrings"))
    print(format % (timeit.timeit(join, number=1000), "join"))
    print(format % (timeit.timeit(join_bytestrings, number=1000), "join_bytestrings"))
    print(format % (timeit.timeit(stringio, number=1000), "stringio"))
    '''
    # benchmark all functions in the local scope
    for key in list(locals().keys()):
        val = locals()[key]
        if key[0] == "_": continue
        if key in ("StringIO", "array"): continue
        if not callable(val): continue
        # print(f"key={key}")
        print(format % (timeit.timeit(val, number=1000), key))
