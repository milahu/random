#!/usr/bin/env bash

# add some onion remotes to this repo

# TODO create new repo on remotes + git push

# clone from onion remote
# $ git -c remote.origin.proxy=socks5h://127.0.0.1:9050 clone ...

owner=milahu
repo="$(dirname "$PWD")"

declare -A remotes
remotes[darktea.onion]=http://it7otdanqu7ktntxzm427cba6i53w6wlanlh23v5i3siqmos47pzhvyd.onion
remotes[righttoprivacy.onion]=http://gg6zxtreajiijztyy5g6bt5o6l3qu32nrg7eulyemlhxwwl6enk6ghad.onion

for name in "${!remotes[@]}"; do
  url="${remotes[$name]}"
  git remote add $name "$url/$owner/$repo"
  # use the system-wide tor proxy at 127.0.0.1:9050
  git config --add remote."$name".proxy socks5h://127.0.0.1:9050
done
