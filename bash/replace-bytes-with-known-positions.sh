#!/usr/bin/env bash

# replace bytes with known positions

# note: if `head -c$n` is not available
# use `dd bs=$n count=1 status=none`

# https://unix.stackexchange.com/questions/346291
# Editing binary streams containing '\x00' bytes

printf 'A\0B\0C\0' |
{
  head -c2 # copy 2 bytes 'A\0'
  head -c1 >/dev/null # skip input byte 'B'
  printf '\x58' # write replacement byte 'X'
  cat # copy the rest '\0C\0'
} |
hexdump -C

# output:
# 00000000  41 00 58 00 43 00                                 |A.X.C.|
