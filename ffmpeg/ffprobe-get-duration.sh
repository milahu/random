#!/bin/sh

# https://trac.ffmpeg.org/wiki/FFprobeTips#Formatcontainerduration

set -e
set -u

for f in "$@"; do

  # duration in float seconds, including milliseconds
  #duration=$(ffprobe -i "$f" -loglevel 0 -of json -show_format | jq -r .format.duration)
  duration=$(ffprobe -i "$f" -loglevel 0 -show_entries format=duration -of default=nw=1:nk=1)

  # get nanoseconds. jq does not support %f or %N format
  duration_ns=${duration#*.}
  if [ "$duration" = "$duration_ns" ]; then
    duration_ns=000000
  fi

  duration_h=$(echo $duration | jq -r 'tonumber | strftime("%H:%M:%S")').$duration_ns

  echo "$duration  $duration_h  $f"

  # human-readable duration
  # less precise because jq cannot format milliseconds or nanoseconds
  # https://github.com/jqlang/jq/issues/1409
  #ffprobe -i "$f" -loglevel 0 -of json -show_format | jq -r '.format.duration | tonumber | strftime("%H:%M:%S.%N")'

done
