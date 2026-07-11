#!/usr/bin/env bash

# https://unix.stackexchange.com/questions/35362
# Creating recursively sorted RAR archive

# https://superuser.com/questions/1492953
# How to RAR files in alphabetical order

# to make this work with all filenames, use zero-delimited file paths

if (($# < 2)); then
  echo "error: not enough arguments"
  echo "usage: $0 [switches] archive.rar input1 [input2 ...]"
  rar
  exit 1
fi

# parse switches
switches=()
while (($# > 0)); do
  case "$1" in
    --)
      shift
      # end of switches
      # stop parsing switches
      break
      ;;
    -*)
      switches+=("$1")
      shift
      ;;
    *)
      # file path of archive or input
      # stop parsing switches
      break
  esac
done

archive_file="$1"
if ! echo "$archive_file" | grep -q -i '\.rar$'; then
  echo "error: archive_file is not a rar file: ${archive_file@Q}"
  exit 1
fi
shift

input_files=()
while (($# > 0)); do
  if ! [ -e "$1" ]; then
    echo "error: missing input file: ${1@Q}"
    exit 1
  fi
  input_files+=("$1")
  shift
done

# note: input files are appended by xargs
rar_args=(rar a "${switches[@]}" "$archive_file")

echo -n "rar command:"; printf " %q" "${rar_args[@]}"; echo

find "${input_files[@]}" -not -type d -print0 |
LANG=C sort -z |
xargs -0 -r "${rar_args[@]}"
