#! /usr/bin/env bash

# ffmpeg-loudnorm-analyze.sh

# analyze loudness of audio streams
# write result to stdout in json format
# keyed by loudnorm result ID
# {"0":{"input_i":"-33.04",...},"1":{...}}

# note: you may want to downmix first to 2ch audio
# to use the final volume of the center channel
# example ffmpeg args:
# -c ac3 -b:a 192k -vol 425 -strict -2 -af "pan=stereo|FL=0.8*FC+0.6*FL+0.6*BL+0.6*SL+0.5*LFE|FR=0.8*FC+0.6*FR+0.6*BR+0.6*SR+0.5*LFE"
# https://superuser.com/a/1420109/951886

# TODO verify ffmpeg output format: Parsed_loudnorm_([0-9]+)

# TODO when is normalization not needed?
# is this good or bad:
# "target_offset" : "0.18"

set -e
set -u

input_file="$1"
shift

# extra args. examples:
# -map 0:a:0 # process only the first audio stream
# -to 10 # process only the first 10 seconds
extra_args=("$@")

# https://ffmpeg.org/ffmpeg-filters.html#loudnorm

ffmpeg -hide_banner -nostdin -i "$input_file" -pass 1 "${extra_args[@]}" \
  -filter:a loudnorm=print_format=json -f null -y /dev/null 2>&1 |
tee -a /dev/stderr |
grep -E '^\[Parsed_loudnorm_([0-9]+) @ 0x[0-9a-f]+\]' -A12 |
sed 's/\t/    /g' |
perl -0777 -pe 's/}\s+\[Parsed_loudnorm_([0-9]+) @ 0x[0-9a-f]+\]\s+/  },\n  "$1": /g' |
perl -0777 -pe 's/\[Parsed_loudnorm_([0-9]+) @ 0x[0-9a-f]+\]\s+/  "$1": /g' |
sed 's/^}/  }/' |
sed '1 i\{'

printf '}\n';
