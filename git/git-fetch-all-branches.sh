#!/usr/bin/env bash

# go from a shallow clone of the main branch
# to a deep clone of all branches

# excluding mounted worktrees is required to avoid errors like
# fatal: refusing to fetch into branch 'refs/heads/master' checked out at '/tmp/repo'

# https://stackoverflow.com/questions/379081/track-all-remote-git-branches-as-local-branches
# https://stackoverflow.com/a/78417326/10440128

remote=${1:-origin}

git fetch $remote --depth=99999999 $(
  git ls-remote --heads $remote |
  cut -d/ -f3- |
  grep -v -x -E $(
    git worktree list --porcelain |
    grep ^branch | cut -c19- | tr $'\n' '|'
  ) |
  sed 's/.*/&:&/'
)
