#!/bin/sh

# gfm = github-flavored markdown

if [ $# = 0 ]; then
  echo "error: no arguments"
  echo "example use:"
  echo "  $0 src.md -o dst.md"
  echo "  $0 src.md | sponge src.md"
  exit 1
fi

exec pandoc --wrap=preserve -f gfm+hard_line_breaks -t gfm "$@"
