#!/usr/bin/env bash
# pnpm-prune-workspace.sh
# workaround for https://github.com/pnpm/pnpm/issues/8307
# use `awk` to parse pnpm-workspace.yaml
# https://pnpm.io/pnpm-workspace_yaml
# and call `pnpm prune` in every package dir
set -eu
shopt -s nullglob
for dir in $(
  awk "
    /^packages:/ { p=1; next }
    p && /^[[:space:]]*(#|$)/ { next }
    p && /^[^[:space:]-]/ { exit }
    p && /^[[:space:]]*-/ {
      gsub(/^[[:space:]]*-[[:space:]]*[\"']?|[\"']?$/, \"\")
      print
    }
  " pnpm-workspace.yaml
); do
  [ -d "$dir" ] || continue
  pushd "$dir"
  echo "pruning $dir/node_modules"
  CI=true pnpm prune --prod --no-optional
  popd
done
