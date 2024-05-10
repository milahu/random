#!/usr/bin/env bash

# usage:
# id3v2-titles-export.sh *.mp3 > titles.txt
# nano titles.txt
# id3v2-titles-import.sh *.mp3 < titles.txt

echo "writing titles of $# files" >&2

for f in "$@"; do
  t="$(
    # id3v2 can fail
    #id3v2 -l "$f" | grep ^TIT2 | cut -c44- |
    #ffprobe -loglevel 0 -of json -show_format "$f" | jq -r .format.tags.title |
    # 10x faster than ffprobe
    sndfile-metadata-get --str-title "$f" | tail -c+26 |
    perl -0777 -pe 's/\n/\\n/g; s/\t/\\t/g; s/\r/\\r/g;'
  )"
  if ((${#t} > 1)); then
    # -2: remove trailing \\n
    t="${t:0: -2}"
  fi
  echo "$f: $t" >&2
  echo "$t"
done
