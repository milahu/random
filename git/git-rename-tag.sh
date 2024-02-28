#!/usr/bin/env bash

# rename git tag and preserve most data
# the old tag is deleted

# push new tag, delete old tag:
# git push origin new_tag :old_tag

# based on https://stackoverflow.com/a/65296616/10440128

set -e

function deref() {
  git for-each-ref "refs/tags/$1" --format="%($2)"
}

function git_tag_rename() {
  local tag1="$1"
  local tag2="$2"
  [ -z "$tag1" ] && return 1
  [ -z "$tag2" ] && return 1
  GIT_COMMITTER_NAME="$(deref $tag1 taggername)" \
  GIT_COMMITTER_EMAIL="$(deref $tag1 taggeremail)" \
  GIT_COMMITTER_DATE="$(deref $tag1 taggerdate)" \
  git tag "$tag2" "$(deref $tag1 '*objectname')" -a -m "$(deref $tag1 contents)" &&
  git tag -d "$tag1"
}

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "usage: $0 tag_1 tag_2" >&2
  exit 1
fi

git_tag_rename "$1" "$2"
