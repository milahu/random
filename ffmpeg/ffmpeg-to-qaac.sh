#!/usr/bin/env bash

# use ffmpeg to decode an audio track to wav format
# and pipe it to qaac to encode it to aac format

# fix qaac error: Not available input file format

# qaac:
# https://github.com/nu774/qaac
# https://github.com/milahu/nur-packages/tree/master/pkgs/applications/audio/qaac

set -e
set -u



# required arguments

input="$1" # example: input.mkv

output="$2" # example: output.m4a



# optional arguments

input_audio_track_id="${3:-0}" # default: 0 = first audio track

# AAC True VBR mode / quality [0-127]
#   0 = lowest  quality = cutoff frequency around  8 KHz # size -70%
#  10 = low     quality = cutoff frequency around 11 KHz # size -65%
#  20 = low     quality = cutoff frequency around 12 KHz # size -60%
#  30 = low     quality = cutoff frequency around 14 KHz # size -55%
#  40 = low     quality = cutoff frequency around 15 KHz # size -50%
#  50 = medium  quality = cutoff frequency around 16 KHz # size -35%
#  60 = medium  quality = cutoff frequency around 17 KHz # size -30%
#  70 = medium  quality = cutoff frequency around 18 KHz # size -23%
#  80 = medium  quality = cutoff frequency around 19 KHz # size -15%
#  90 = default quality = cutoff frequency around 20 KHz
# 100 = high    quality = cutoff frequency around 21 KHz # size +13%
# 110 = high    quality = cutoff frequency around 22 KHz # size +37%
# 120 = high    quality = cutoff frequency around 23 KHz # size +50%
# 127 = highest quality = cutoff frequency around 24 KHz # size +66%
output_vbr_quality="${4:-90}"

# AAC encoding Quality [0-2]
# 0 = hard cutoff = low quality
# 1 = soft cutoff = high quality
# 2 = soft cutoff = higher quality
output_aac_quality="${5:-2}"



# print ffmpeg version
ffmpeg -version | head -n1

# tmp_format=wav
tmp_format=caf

set -x

ffmpeg -hide_banner -nostdin -loglevel warning \
  -i "$input" -map 0:a:"$input_audio_track_id" -f $tmp_format - |
qaac --tvbr "$output_vbr_quality" --quality "$output_aac_quality" -o "$output" -
