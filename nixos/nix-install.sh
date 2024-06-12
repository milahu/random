#!/usr/bin/env bash
# install static build of nix
# useful for running nix as an unprivileged user
# https://zameermanji.com/blog/2023/3/26/using-nix-without-root/
set -eux
# get latest nix version
nix_version=$(
  git ls-remote --tags https://github.com/NixOS/nix |
  cut -d/ -f 3 | grep -v '}$' | sort --version-sort | tail -n1
)
# use only major and minor version, for example 2.22
nix_version_12=${nix_version%.*}
nix_url="https://hydra.nixos.org/job/nix/maintenance-$nix_version_12/"
nix_url+="buildStatic.x86_64-linux/latest/download-by-type/file/binary-dist"
curl --fail -o ~/bin/nix.tmp -L "$nix_url"
mv ~/bin/nix.tmp ~/bin/nix
chmod +x ~/bin/nix
