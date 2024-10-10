#!/bin/sh

# example results: stereo 3.1 5.1 7.1
# print one line for each audio stream

set -e
set -u

src="$1"
shift

# parse extra args
streams=a # all audio streams
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
    echo "error: unrecognized argument: ${1@Q}"
    exit 1
    continue
    ;;
esac; done

res=$(ffprobe -loglevel error -select_streams $streams -show_entries stream=channel_layout -of default=nw=1:nk=1 "$src")

if [ -z "$res" ]; then
  exit 1
fi

echo "$res"
