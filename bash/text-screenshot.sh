#! /usr/bin/env bash

# text screenshot
# capture the visible output of a process
# https://unix.stackexchange.com/a/697804/295986

captureCommand="$(cat <<'EOF'
  # example: progress bar
  # https://stackoverflow.com/a/23630781/10440128
  for ((i=0; i<100; i++)); do
    sleep 0.1
    printf .
  done | pv -p -c -s 100 -w 40 > /dev/null
EOF
)"
# note: to stop the captureCommand after some time
# you can wrap it in `timeout -k 60 60`
# to stop after 60 seconds
# or use `for waiterStep in $(seq 0 60)`
# in the waiter loop

# create a new screen session. dont attach
screenName=$(mktemp -u screen-session-XXXXXXXX)
screen -S "$screenName" -d -m

# create lockfile
screenLock=$(mktemp /tmp/screen-lock-XXXXXXXX)
# remove lockfile after captureCommand
screenCommand="$captureCommand; rm $screenLock;"

echo "start captureCommand"
# send text to detached screen session
# ^M = enter
screen -S "$screenName" -X stuff "$screenCommand^M"
hardcopyFile=$(mktemp /tmp/hardcopy-XXXXXXXX)

enableWatcher=true
if $enableWatcher; then
  echo "start watcher"
  (
    # watcher: show live output while waiting
    while true
    #for watcherStep in $(seq 0 100) # debug
    do
      sleep 2
      # take screenshot. -h = include history
      screen -S "$screenName" -X hardcopy -h "$hardcopyFile"
      cat "$hardcopyFile"
    done
  ) &
  watcherPid=$!
fi

echo "wait for captureCommand ..."
while true
#for waiterStep in $(seq 0 60) # debug
do
  sleep 1
  [ -e "$screenLock" ] || break
done
echo "done captureCommand"

if $enableWatcher; then
  kill $watcherPid
fi

# take a last screenshot
screen -S "$screenName" -X hardcopy -h "$hardcopyFile"
echo "done hardcopy $hardcopyFile"

# kill the detached screen session
screen -S "$screenName" -X quit
