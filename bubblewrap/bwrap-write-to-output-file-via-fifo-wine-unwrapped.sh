#!/usr/bin/env bash

# bwrap-write-to-output-file-via-fifo-wine-unwrapped.sh

# this works
# but this fails with bwrap
# see bwrap-write-to-output-file-via-fifo-wine.sh

cat >/dev/null <<'EOF'
FIXME echo says "Invalid function." when writing to fifo, but it works

wine/po/wine.pot
#: dlls/kernelbase/winerror.mc:33
msgid "Invalid function.\n"
msgstr ""

wine/dlls/kernelbase/winerror.mc
MessageId=1
SymbolicName=ERROR_INVALID_FUNCTION
Language=ENU
Invalid function.
.

TODO why does wine return ERROR_INVALID_FUNCTION
EOF



set -e

sandbox="$(
cat <<'EOF'
@echo off
:: write "hello" to %1
echo in_sandbox: writing to %1
echo hello > %1
EOF
)"

sandbox_file=$(mktemp -u sandbox.XXXXXXXXX.bat)
echo "$sandbox" >$sandbox_file

#set -x # debug

out_pipe=$(mktemp -u out_pipe.XXXXXXXXXXXXX)
out_file=$(mktemp -u out_file.XXXXXXXXXXXXX)

echo "creating pipe $out_pipe"
mkfifo $out_pipe

echo "writing from pipe to $out_file"
cat $out_pipe >$out_file &
writer_pid=$!

wine_args=(
  wine
  # not working: cmd.exe /c "$sandbox" sandbox
  $sandbox_file
  $out_pipe
)

set -x # debug
"${wine_args[@]}"
set +x

echo "removing pipe $out_pipe"
rm $out_pipe

# not necessary? No such process
#echo "killing writer $writer_pid"
#kill $writer_pid

echo "output received from sandbox:"
cat $out_file
rm $out_file

rm $sandbox_file
