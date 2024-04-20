#!/usr/bin/env bash

# bwrap-write-to-output-file-via-dir-wine.sh

# this works

set -e

sandbox="$(
cat <<'EOF'
@echo off
echo in_sandbox: writing to %1
echo hello >%1
EOF
)"

sandbox_file=$(mktemp -u /run/user/$(id -u)/sandbox.XXXXXXXXX.bat)
echo "$sandbox" >$sandbox_file

#set -x # debug

temp_dir=$(mktemp -d temp_dir.XXXXXXXXXXXXX)
out_file=$temp_dir/out_file

# get prefix of wine
wine=$(dirname $(dirname $(readlink -f $(which wine))))

export WINEPREFIX=$HOME/.wine
# disable wine error messages by default
export WINEDEBUG="${WINEDEBUG:=-all}"
# disable wine GUI
unset DISPLAY

# make it work in bubblewrap
# fix: wine: could not load ntdll.so
# https://unix.stackexchange.com/a/670754/295986
#export WINEDLLPATH=$wine/lib/wine/x86_64-unix # wine64
export WINEDLLPATH=$wine/lib/wine/i386-unix/ # wine

bwrap_args=(
  bwrap
  --tmpfs /tmp
  --ro-bind /nix/store /nix/store

  # relative path breaks:
  # in_sandbox: writing to temp_dir.HsfbhmeBolSFW/out_file
  # Path not found.
  #--bind $temp_dir $temp_dir
  --bind $(realpath $temp_dir) $(realpath $temp_dir)

  --bind $WINEPREFIX $WINEPREFIX
  --bind $sandbox_file $sandbox_file
  --setenv WINEPREFIX $WINEPREFIX
  --setenv WINEDLLPATH $WINEDLLPATH
  --
  $wine/bin/wine
  # not working: cmd.exe /c "$sandbox" sandbox
  $sandbox_file
  $out_file
)

#set -x # debug
"${bwrap_args[@]}"

echo "output received from sandbox:"
cat $out_file
rm $out_file
rmdir $temp_dir

rm $sandbox_file
