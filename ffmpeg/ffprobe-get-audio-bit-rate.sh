#!/bin/sh

# example results: stereo 3.1 5.1 7.1
# print one line for each audio stream

set -e
set -u

#src="$1"
#shift

# parse extra args
streams=a # all audio streams
files=()
while [ $# != 0 ]; do case "$1" in
  -map)
    if ! echo "$2" | grep -q -E -x '0:a:[0-9]+'; then
      echo "error: unrecognized map argument: ${2@Q}. expected something like 0:a:0 or 0:a:1"
      exit 1
    fi
    streams="${2:2}" # 0:a:0 -> a:0
    shift 2
    continue
    ;;
  *)
    #echo "error: unrecognized argument: ${1@Q}"
    #exit 1
    files+=("$1")
    shift
    continue
    ;;
esac; done

#exec ffprobe -loglevel error -select_streams $streams -show_streams -of json "$src"
#            "sample_fmt": "s32",
#            "sample_rate": "44100",

for src in "${files[@]}"; do

  #set -x

  res=$(ffprobe -loglevel error -select_streams $streams -show_entries stream=bit_rate -of default=nw=1:nk=1 "$src")

  if [ "$res" = "N/A" ]; then
    # TODO get average bitrate
    # trust BPS tag...
    res=$(ffprobe -loglevel error -select_streams $streams -show_streams -of json "$src")
    res=$(echo "$res" | jq -r '.streams[0].tags."BPS-eng"')
  fi

  echo "$res $src"

done
