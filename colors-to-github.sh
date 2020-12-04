#!/bin/bash

# convert ansi-colored terminal output to github markdown

# to colorize text on github, we use <span color="red">red</span> etc
# depends on: aha, xclip
# license: CC0-1.0
# sample use: colors-to-github.sh diff a.txt b.txt

cmd="$1"
shift

# add arguments to force color output
# TODO add more commands here
extra_args=''
if [[ ' diff ls cargo ' =~ " $cmd " ]]; then
    extra_args='--color=always'
elif [[ ' jp2a ' =~ " $cmd " ]]; then
    extra_args='--colors'
elif [[ ' gulp ' =~ " $cmd " ]]; then
    extra_args='--color'
elif [[ ' npm ' =~ " $cmd " ]]; then
    extra_args='--color always'
fi

(
    echo '<pre>'
    "$cmd" $extra_args "$@" 2>&1 | aha --no-header
    echo '</pre>'
) \
| sed -E 's/<span style="[^"]*color:([^;"]+);"/<span color="\1"/g' \
| sed -E 's/ style="[^"]*"//g' \
| xclip -i -sel clipboard

echo 'output is in clipboard. hit control + V in your editor'
