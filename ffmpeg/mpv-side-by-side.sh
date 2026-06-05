#!/usr/bin/env bash

# https://github.com/mpv-player/mpv/issues/3854
# Play multiple videos sides by sides

# TODO crop=w:h:x:y
# mpv somevideo720.mkv --external-file=somevideo1080.mkv --lavfi-complex='[vid1] scale=960x540 [vid1_scale]; [vid2] scale=960x540 [vid2_scale]; [vid1_scale][vid2_scale] hstack [vo]'

# TODO rewrite in python

set -e
set -u

function ffprobe-get-video-resolution() {
  ffprobe -i "$1" -loglevel 0 -select_streams v -show_streams -of json | jq -r '"\(.streams[0].width)x\(.streams[0].height)"'
}

IFS=x read w1 h1 < <(ffprobe-get-video-resolution "$1")
IFS=x read w2 h2 < <(ffprobe-get-video-resolution "$2")

echo "w1: $w1"; echo "h1: $h1"
echo "w2: $w2"; echo "h2: $h2"

border=5

scale1f=
scale2f=

delay1=${3:-0} # can be positive or negative
# delay2=${4:-0}

delay1f="setpts=PTS+${delay1}/TB ,"
# delay2f="setpts=PTS+${delay2}/TB ,"
delay2f=

if [ "$w1" = "$w2" ]; then
  # same width
  if [ "$h1" = "$h2" ]; then
    # same resolution
    crop1="$((w1 / 2 + border)):$h1:0:0"
    crop2="$((w2 / 2 + border)):$h2:$((w2 / 2 + border)):0"
  else
    # same width, diff height
    if (( h1 < h2 )); then
      # h1 is smaller
      y2=$(( (h2 - h1) / 2 ))
      crop1="$((w1 / 2 + border)):$h1:0:0"
      crop2="$((w2 / 2 + border)):$h1:$((w2 / 2 + border)):$y2"
    else
      # h2 is smaller
      y1=$(( (h1 - h2) / 2 ))
      crop1="$((w1 / 2 + border)):$h2:0:$y1"
      crop2="$((w2 / 2 + border)):$h2:$((w2 / 2 + border)):0"
    fi
  fi
else
  # choose a common height (avoid upscaling)
  target_h=$(( h1 < h2 ? h1 : h2 ))

  # scale both videos to same height
  scale1f="scale=-2:${target_h} ,"
  scale2f="scale=-2:${target_h} ,"

  # compute resulting widths after scaling
  scaled_w1=$(( w1 * target_h / h1 ))
  scaled_w2=$(( w2 * target_h / h2 ))

  # crop halves (same logic as before, but now valid)
  crop1="$((scaled_w1 / 2 + border)):${target_h}:0:0"
  crop2="$((scaled_w2 / 2 + border)):${target_h}:$((scaled_w2 / 2 + border)):0"
fi

filter="$(
  echo "[vid1] $delay1f $scale1f crop=$crop1 [vid1_crop];"
  echo "[vid2] $delay2f $scale2f crop=$crop2 [vid2_crop];"
  echo "[vid1_crop][vid2_crop] hstack [vo];"
)"

set -x
exec mpv "$1" --external-file="$2" --lavfi-complex="$filter"
