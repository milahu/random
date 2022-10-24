#! /bin/sh

# devloop.sh
# run command in infinite loop
# wait before restarting, to allow stopping the loop
# license: MIT, author: milahu
# https://stackoverflow.com/questions/15785522/catch-sigint-in-bash-handle-and-ignore

restart_delay=2

command="$1" # TODO use all args: $@

if [ -z "$command" ]
then
  command="( set -x; sleep 5 ); false # example command: sleep 5 seconds, set rc=1"
  # example: drop cache, run vite
  #command="rm -rf node_modules/.vite/ ; npx vite --clearScreen false"
fi

loop_next() {

  echo
  echo "starting command. hit Ctrl+C to restart"
  echo "  $command"

  (eval "$command") &
  command_pid=$!

  #echo "main pid: $$"; echo "cmd  pid: $command_pid" # debug

  restart_command() {
    echo
    echo "restarting command in $restart_delay seconds. hit Ctrl+C to stop"
    sleep $restart_delay
    loop_next # recursion
  }

  stop_command() {
    echo
    echo "got Ctrl+C -> stopping command"
    kill $command_pid
    trap exit SIGINT # handle second Ctrl+C
    restart_command
  }

  trap stop_command SIGINT # handle first Ctrl+C

  wait $command_pid # this is blocking

  echo "command stopped. return code: $?"
  restart_command
}

echo starting loop
loop_next
