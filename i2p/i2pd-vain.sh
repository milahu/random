#!/bin/sh
# i2pd-vain.sh
# parse the output of i2pd-tools vain and rename output files
# example use: i2pd-vain.sh someprefix -m -t8
# https://github.com/PurpleI2P/i2pd-tools/issues/104
set -eu
vain "$@" |
while read -r line; do
  echo "$line"
  case "$line" in
    Address\ found\ *)
      # Address found xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx in 5
      address=${line%\ in\ *}
      address=${address#*\ *\ }
      ;;
    outpath\ for\ a\ now*)
      # outpath for a now: private3.dat
      outpath=${line##*\ }
      mv -v "$outpath" "$address.dat"
      ;;
  esac
done
