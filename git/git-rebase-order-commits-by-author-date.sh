#!/usr/bin/env bash

# git-rebase-order-commits-by-author-date.sh

# https://stackoverflow.com/questions/27245008/reorder-git-commit-history-by-date

if [ $# = 0 ]; then
  echo "usage:" >&2
  echo "  $0 git_rebase_args..." >&2
  echo "" >&2
  echo "examples:" >&2
  echo "  $0 HEAD~5" >&2
  echo "  $0 --root --committer-date-is-author-date" >&2
  exit 1
fi

if [ $# = 1 ] && [ -e "$1" ] && [ "${1: -34}" == "/.git/rebase-merge/git-rebase-todo" ]; then

  # arg is commit list file
  # this script was called via sequence.editor
  todo_path="$1"
  todo_text=$(grep "^pick " "$todo_path")
  echo "$todo_text" | sort -k3 >"$todo_path"
  exit

fi

# %at = author timestamp
# the todo file will have 3 columns:
# pick $hash $timestamp

git \
  -c rebase.instructionFormat="%at" \
  -c sequence.editor="$0" \
  rebase -i "$@"
