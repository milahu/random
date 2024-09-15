#!/bin/sh

# find newest file

# fast "streaming" solution
# https://stackoverflow.com/a/4562154/10440128
d="${1:-.}"
find "$d" -type f -printf "%T@\0%p\0" | awk '{ if ($0>x) {x=$0; getline z} else getline } END {print z}' RS='\0'

# fast "streaming" solution
# https://stackoverflow.com/a/36023755/10440128
#find "$d" -type f -printf '%T@ %p\n' | perl -ne '@a=split(/\s+/, $_, 2); ($t,$f)=@a if $a[0]>$t; print $f if eof()'

# slow "buffering" solution
# show the "top 10" of newest files
# https://stackoverflow.com/a/7448828/10440128
#find "$d" -type f -print0 | xargs -0 stat --format '%Y :%y %n' | sort -nr | cut -d: -f2- | head -n10
