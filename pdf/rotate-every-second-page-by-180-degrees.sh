#!/bin/sh

set -eux

# rotate all even pages by 180 degrees
exec pdftk "$1" rotate 1-endevendown output "$1.rotated.pdf"

# rotate all odd pages by 180 degrees
# exec pdftk "$1" rotate 1-endodddown output "$1.rotated.pdf"
