#!/bin/sh

# gfm = github-flavored markdown

if [ $# = 0 ]; then
  echo "error: no arguments"
  echo "example use:"
  echo "  $0 src.md -o dst.md"
  echo "  $0 -i src.md"
  echo "  $0 src.md | sponge src.md"
  exit 1
fi

if [ $# = 2 ] && [ "$1" = "-i" ]; then
  echo "editing in-place: $2" >&2
  # sponge fails if $TMP directory does not exist
  mkdir -p $TMP
  pandoc --wrap=preserve -f gfm+hard_line_breaks -t gfm "$2" | sponge "$2"
  exit $?
fi

exec pandoc --wrap=preserve -f gfm+hard_line_breaks -t gfm "$@"
