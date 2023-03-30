#! /bin/sh
# binary-grep.sh
# find offset of one small binary file
# inside another large binary file
# license: public domain
# https://unix.stackexchange.com/questions/39728

if [ $# != 2 ]; then
  echo "usage: $0 needle.bin haystack.bin" >&2
  exit 1
fi

needle="$1"
haystack="$2"

# the order of the files $haystack and $needle
# matters for performance

xdelta3 -e -s "$haystack" "$needle" /dev/stdout |
xdelta3 printhdrs /dev/stdin |
grep "VCDIFF copy window offset" | cut -c 31-
