#!/usr/bin/env bash

# scripts/git-remote-add.sh

set -eux

owner=$(cat ~/.git-credentials | grep '@github\.com$' | sed -E 's|https://([^:]+):.*$|\1|')
if [ -z "$owner" ]; then
  echo "error: failed to parse repo owner from ~/.git-credentials"
  exit 1
fi

cd "$(dirname "$0")/.."
repo=$(basename "$PWD")

function git_remote_add_onion() {
  local remote="$1"
  local url="$2"
  git remote add "$remote" "$url" ||
  git remote set-url "$remote" "$url"
  git config --add remote."$remote".proxy socks5h://127.0.0.1:9050
}

remote=darktea.onion
url=http://it7otdanqu7ktntxzm427cba6i53w6wlanlh23v5i3siqmos47pzhvyd.onion/$owner/$repo
git_remote_add_onion "$remote" "$url"

remote=righttoprivacy.onion
url=http://gg6zxtreajiijztyy5g6bt5o6l3qu32nrg7eulyemlhxwwl6enk6ghad.onion/$owner/$repo
git_remote_add_onion "$remote" "$url"
