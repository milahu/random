#!/usr/bin/env bash

# bwrap-write-to-output-file-via-fifo.sh

# this works

set -e

sandbox="$(
cat <<'EOF'
out="$1"
#echo "$0: args: $@"
echo "$0: writing to $out"
echo hello >"$out"
EOF
)"

#set -x # debug

out_pipe=$(mktemp -u out_pipe.XXXXXXXXXXXXX)
out_file=$(mktemp -u out_file.XXXXXXXXXXXXX)

echo "creating pipe $out_pipe"
mkfifo $out_pipe

echo "writing from pipe to $out_file"
cat $out_pipe >$out_file &
writer_pid=$!

bwrap_args=(
  bwrap
  --tmpfs /tmp
  --ro-bind /nix/store /nix/store
  --bind $out_pipe $out_pipe
  --
  $(which bash)
  -c "$sandbox"
  sandbox
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
