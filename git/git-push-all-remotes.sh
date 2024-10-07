#!/usr/bin/env bash

set -x

# the "onion or not" logic assumes
# that onion remotes have a name ending with ".onion"
# example:
# git remote add darktea.onion http://it7otdanqu7ktntxzm427cba6i53w6wlanlh23v5i3siqmos47pzhvyd.onion/milahu/random

# non-onion remotes
for remote in $(git remote show | grep -v '\.onion$'); do
  git push $remote "$@"
done

# onion remotes
for remote in $(git remote show | grep '\.onion$'); do
  git push $remote "$@"
done
