#!/bin/sh

set -e
set -u

# todo whats the diff?
# json.streams[0].coded_width = 1280;
# json.streams[0].width = 1280;
ffprobe -i "$1" -loglevel 0 -select_streams v -show_streams -of json | jq -r '"\(.streams[0].width)x\(.streams[0].height)"'
#ffprobe -i "$1" -loglevel 0 -select_streams v -show_streams -of json | jq -r '"\(.streams[0].coded_width)x\(.streams[0].coded_height)"'
