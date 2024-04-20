#!/usr/bin/env bash

# insert-random-string-in-middle-of-filename.sh

insert_random_string_in_middle_of_filename() {
  local name=$(basename "$1")
  local len=${#name}
  #local maxlen=255 # hard limit on ext4. lower on other filesystems (iso9660)
  local maxlen=100 # soft limit
  local minlen=20
  local rndlen=16
  local rnd=$(</dev/random base64 | tr -d '+/' | head -c $rndlen)
  local maxlen2=$((maxlen - rndlen))
  if [ $len -lt $minlen ]; then
    # preserve file extension
    echo "${name}_${rnd}_${name}"
    return
  fi
  if [ $len -lt $maxlen2 ]; then maxlen2=$len; fi
  local half=$((maxlen2 / 2))
  echo "${name:0:$half}_${rnd}_${name: -$half}"
}

# demo
for len in 1 2 3 4 5 10 20 21 50 51 100 101 200 201 500 501 1000 1001; do
  filename=$(while true; do echo -n 1234567890; done | head -c$len)
  printf "len %5d: " $len
  insert_random_string_in_middle_of_filename /path/to/$filename
done
