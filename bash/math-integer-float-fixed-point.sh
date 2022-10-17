#! /usr/bin/env bash

# bash: convert between integer and float numbers in pure bash,
# without calling any external binaries, to avoid context switching

# note: ${a:1} is a bashism
# this works only in bash, not in posix shells (dash, posh)

# based on https://github.com/tartley/rerun2/pull/12

# run online https://replit.com/@milahu/math-integer-float-sh

# my motivation is to avoid the dependency
# for example, on nixos linux, bc is not installed by default

# performance is not relevant
# as this code executes only all 0.25 seconds or so

# see also

# How do I use floating-point arithmetic in bash
# https://stackoverflow.com/a/35402635/10440128

# Fixed-point arithmetic
# https://en.wikipedia.org/wiki/Fixed-point_arithmetic

for msecs in "" 0 1 12 123 1234 12345 123456 1234567 12345678 123456789
do

  # int msecs -> float secs
  a=000$msecs
  a=${a:0: -3}
  while [ "${a:0:1}" = 0 ]; do a=${a:1}; done
  if [ -z "$a" ]; then a=0; fi
  b=000$msecs
  b=${b: -3}
  secs=$a.$b

  if [[ "$msecs" == "" ]]
  then
    printf '%-10s %10s\n' "(empty)" $secs
  else
    printf '%-10s %10s\n' $msecs $secs
  fi

done
