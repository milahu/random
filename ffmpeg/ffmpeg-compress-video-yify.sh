#! /usr/bin/env bash

# compress video to small size
# based on https://gist.github.com/kuntau/a7cbe28df82380fd3467
# docs: https://trac.ffmpeg.org/wiki/Encode/H.264
# docs: https://trac.ffmpeg.org/wiki/Encode/HighQualityAudio
# note: this is slow. about 0.1x to 0.5x
# note: here we do no resizing/scaling. example: 720p input -> 720p output
# todo: downmix 5.1 to 2.0

input="$1"
output="$1.mp4"

x264_params=""
x264_params+="cabac=1:ref=5:analyse=0x133:me=umh:subme=9:chroma-me=1:deadzone-inter=21"
x264_params+=":deadzone-intra=11:b-adapt=2:rc-lookahead=60:vbv-maxrate=10000:vbv-bufsize=10000:qpmax=69"
x264_params+=":bframes=5:b-adapt=2:direct=auto:crf-max=51:weightp=2:merange=24:chroma-qp-offset=-1"
x264_params+=":sync-lookahead=2:psy-rd=1.00,0.15:trellis=2:min-keyint=23:partitions=all"

args=(
  ffmpeg
  -hide_banner
  -i "$input"
  -c:v libx264 -crf 27 -x264-params "$x264_params"
  -c:a libopus -b:a 128k
  -map 0
  -map_metadata 0
  -movflags +faststart
  "$output"
)

set -x
exec "${args[@]}"
