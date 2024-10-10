#!/bin/sh

set -e
set -u

#ffprobe -i "$1" -loglevel 0 -select_streams v -show_streams -of json | jq -r '.streams.avg_frame_rate'
ffprobe -i "$1" -loglevel 0 -select_streams v -show_entries stream=avg_frame_rate -of default=nw=1:nk=1

# https://trac.ffmpeg.org/ticket/10954
# ffprobe -select_streams v -show_entries stream=avg_frame_rate -of csv test.mp4
#!/bin/sh

set -e
set -u

# https://stackoverflow.com/a/64251589/10440128
#ffprobe -loglevel error -select_streams v -show_entries stream=codec_name -of default=nw=1:nk=1 "$1"
