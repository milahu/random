#!/usr/bin/env bash

qs="1 2 5 10 15 25 30 35"

for src in "$@"; do
  for q in $qs; do
    dst="$src".q$(printf %03d $q).webp
    [ -e "$dst" ] && continue
    magick "$src" -quality $q% "$dst"
  done
done
