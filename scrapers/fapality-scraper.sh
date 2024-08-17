#!/usr/bin/env bash

# fapality scraper
# download all images from a photo album

# see also
# https://github.com/search?q=fapality+scraper+language%3APython&ref=opensearch&type=code&l=Python

set -eux

#index_url="https://fapality.com/photos/24/70-tasty-amateur-assholes/"

for index_url in "$@"; do

  index_url=$(echo "$index_url" | sed -E 's|/image[0-9]+/$|/|')

  path="$HOME/Pictures/porn/${index_url:8}"
  mkdir -p "$path"
  cd "$path"

  #index_html=$(curl -s "$index_url")
  if ! [ -e index.html ]; then
    curl -o index.html "$index_url"
  fi

  #first_url=$(grep -o -E 'https://i[0-9]+.fapality.com/contents/albums/sources/[0-9]+/[0-9]+/[0-9]+.jpg' index.html)
  first_url=$(grep -o -E 'https://i[0-9]+.fapality.com/contents/albums/[^"]+/[0-9]+.jpg' index.html | sed -E 's|/main/[0-9]+x[0-9]+/|/sources/|' | sort -n -u | head -n1)

  #num_pics=$(grep -o -E ' - pic 1 of [0-9]+</h1>' index.html | sed -E 's| - pic 1 of ([0-9]+)</h1>|\1|')
  num_pics=$(grep -o -E ' - [0-9]+ pics</title>' index.html | sed -E 's| - ([0-9]+) pics</title>|\1|')

  echo "first_url: $first_url"
  echo "num_pics: $num_pics"

  first_num=$(echo "$first_url" | sed -E 's|^.*/([0-9]+)(\.[a-z]+)$|\1|')
  file_ext=$(echo "$first_url" | sed -E 's|^.*/([0-9]+)(\.[a-z]+)$|\2|')
  last_num=$((first_num + num_pics))
  url_pattern=$(dirname "$first_url")/"[$first_num-$last_num]$file_ext"
  #url_pattern='https://i5.fapality.com/contents/albums/sources/0/24/[456-525].jpg'

  echo "downloading $num_pics pics"
  curl -s -N -O "$url_pattern"

  echo "done $path"

done
