#!/usr/bin/env bash

set -eux

# downmix audio to stereo
# write video to mp4 file

# part of
# video release script
# https://github.com/milahu/todo#video-release-script

# todo two pass loudnorm
# 1. downmix to wav to stdout
# 2. loudnorm analyze to json
# 3. downmix + loudnorm

# fixme this script requires
# other scripts in $d
# but should be self contained
d="$(dirname "$0")"

# todo parse options like "-ac 1"

# loop input files
for i in "$@"; do

o="$i.2ch.mp4"

# get audio channel layout
# note: use first audio channel
# todo: select ac by language
get_acl="$d/ffprobe-get-audio-channel-layout.sh"
#acl=5.1
#acl=$("$get_acl" "$i")
acl=$("$get_acl" "$i" | head -n1)
echo "acl: ${acl@Q}"
sleep 1

# downmix to stereo
# todo handle noop case: input is stereo
get_af="$d/downmix-audio-to-stereo-rfc7845.py"
af=$("$get_af" "$acl")
echo "af: ${af@Q}"
sleep 1

a=(
  ffmpeg
  -hide_banner
  -nostdin
  -i "$i"
  -c:v copy
  -c:a aac
  -movflags faststart # mp4 stream
)
if [ -n "$af" ]; then
echo "downmixing to stereo"
a+=(
  -af "$af"
)
else
echo "not downmixing to stereo"
fi
a+=(
  -y
  "$o"
)
set -x
"${a[@]}"
set +x

done
