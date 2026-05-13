#!/usr/bin/env bash

set -e
set -u
set -x # debug

# remove devDependencies and optionalDependencies from node_modules
# # npm prune --omit=dev --omit=optional --verbose --debug --offline
# but we have no package-lock.json, so "npm prune" requires internet access
# and "yarn prune" does not exist
# fix: implement "npm prune" in bash

npmPruneArgs="--omit=dev --omit=optional"

echo "pruning node_modules"
mkdir node_modules_prod
# +15: also remove prefix "e/node_modules/"
npm ls --all --parseable $npmPruneArgs |
tail -n+2 |
cut -c$((${#PWD}+15))- |
while read -r pkg
do
    # pkg: @some/package
    src="node_modules/$pkg"
    dst="node_modules_prod/$pkg"
    # echo "> cp -r $src $dst"
    mkdir -p "${dst%/*}"
    cp -a "$src" "$dst"
done
echo "done node_modules_prod"
