#!/usr/bin/env bash

echo "reading titles for $# files"

title_list=()
while read line; do
  t="$(
    echo -n "$line" |
    perl -0777 -pe 's/\\n/\n/g; s/\\t/\t/g; s/\\r/\r/g;'
  )"
  #echo "t: $t" >&2
  title_list+=("$t")
done

if [ $# != ${#title_list[@]} ]; then
  echo "error: number mismatch. $# files vs ${#title_list[@]} titles"
  exit 1
fi

echo "tagging $# files"

i=0
while [ $# != 0 ]; do
  echo "i $i"
  f="$1"
  shift
  t="${title_list[$i]}"
  i=$((i + 1))
  #echo tageditor set title="$t" --id3v1-usage never -f "$f"
  tageditor set title="$t" --id3v1-usage never -f "$f"
done
