#!/bin/sh

set -e
set -u

# https://stackoverflow.com/a/64251589/10440128
ffprobe -loglevel error -select_streams v -show_entries stream=codec_name -of default=nw=1:nk=1 "$1"
