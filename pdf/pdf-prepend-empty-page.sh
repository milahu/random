#!/usr/bin/env bash

# prepend an empty page to a PDF document
# useful for printing, to swap even and odd pages

# based on

# https://unix.stackexchange.com/questions/15992
# How do I insert a blank page into a PDF with ghostscript or pdftk?

# https://unix.stackexchange.com/questions/277892
# How do I create a blank PDF from the command line?

set -eux

src="$1"
dst="$2"

# parse "Page size:       396 x 612 pts"
read _ _ x _ y _ < <(pdfinfo "$src" | grep "^Page size:")
echo "page size: x=$x y=$y"

page="${x}x${y}"

# no, we need a tempfile for pdftk
# https://unix.stackexchange.com/questions/798853
# java.io.IOException: Illegal seek
# pdftk <(magick xc:none -page $page pdf:-) "$src" cat output "$dst"

blank_pdf=$(mktemp -p /run/user/$UID --dry-run --suffix=.blank.pdf)

magick xc:none -page $page $blank_pdf

pdftk "$blank_pdf" "$src" cat output "$dst"

rm "$blank_pdf"

echo "done ${dst@Q}"
