#!/bin/sh

ffprobe-get-duration.sh "$@" | awk '{ print $1 }' | LC_ALL=C datamash sum 1
