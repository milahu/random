#!/bin/sh

set -e
set -u

ffprobe -loglevel error -show_entries format=format_name -of default=nw=1:nk=1 "$1"
