#! /usr/bin/env bash

input="input.mkv"
output="output.mkv"

# -c:a libopus -b:a 128k \
# -map 0 \

# TODO normalize audio volume

# compress audio
# ffmpeg-to-qaac.sh
tmp_audio="$output.a0.m4a"
input_audio_track_id=0
#  90 = default quality = cutoff frequency around 20 KHz
output_vbr_quality=90
output_aac_quality=2
ffmpeg -hide_banner -nostdin -loglevel warning \
  -i "$input" -map 0:a:"$input_audio_track_id" -f caf - |
qaac --tvbr "$output_vbr_quality" --quality "$output_aac_quality" -o "$tmp_audio" -

# compress video
# https://ffmpeg.party/guides/x265/
ffmpeg \
-hide_banner \
-hwaccel auto \
-i "$input" \
-i "$tmp_audio" \
-map 0:v \
-map 1:a \
-c:v libx265 \
-crf 28 \
-preset medium \
-x265-params no-open-gop=1:keyint=300:gop-lookahead=12:bframes=6:weightb=1:hme=1:strong-intra-smoothing=0:rect=0:aq-mode=4 \
-c:a copy \
-movflags +faststart \
"$output"
