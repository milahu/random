#!/usr/bin/env bash

set -eux

branch_name="$1"

exec git worktree add --orphan -b "$branch_name" "$branch_name"
