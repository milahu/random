#!/usr/bin/env bash

# bwrap-write-to-output-file-via-fifo-wine.sh

# this fails
# FIXME output from sandbox is not received
# echo "output received from sandbox:"

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

out_pipe=$(mktemp -u out_pipe.XXXXXXXXXXXXX)
out_file=$(mktemp -u out_file.XXXXXXXXXXXXX)

echo "creating pipe $out_pipe"
mkfifo $out_pipe

echo "writing from pipe to $out_file"
cat $out_pipe >$out_file &
writer_pid=$!

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
  --bind $out_pipe $out_pipe
  --bind $WINEPREFIX $WINEPREFIX
  --bind $sandbox_file $sandbox_file
  --setenv WINEPREFIX $WINEPREFIX
  --setenv WINEDLLPATH $WINEDLLPATH
  --
  $wine/bin/wine
  # not working: cmd.exe /c "$sandbox" sandbox
  $sandbox_file
  $out_pipe
)

#set -x # debug
"${bwrap_args[@]}"

echo "removing pipe $out_pipe"
rm $out_pipe

# not necessary? No such process
#echo "killing writer $writer_pid"
#kill $writer_pid

echo "output received from sandbox:"
cat $out_file
rm $out_file

rm $sandbox_file
