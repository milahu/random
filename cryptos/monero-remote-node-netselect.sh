#!/usr/bin/env bash

# show the top 10 of monero remote nodes
# https://monero.fail/
# https://www.getmonero.org/resources/user-guides/remote_node_gui.html

list_url=https://monero.fail/haproxy.cfg
list_path=$HOME/.cache/monero.fail/haproxy.cfg
top_n=10
test_time=10

mkdir -p ${list_path%/*}

if [ -e "$list_path" ]; then
  ctime=$(stat -c%W "$list_path")
  now=$(date --utc +%s)
  age=$((now - ctime))
  if ((age > 10*24*60*60)); then
    echo "deleting old server list"
    rm "$list_path"
  fi
fi

if ! [ -e "$list_path" ]; then
  echo "fetching server list"
  curl -o "$list_path" "$list_url"
fi

echo "note: netselect requires root access"

cat "$list_path" |
grep "^    server " |
cut -d" " -f7 |
grep -v -E '\.(i2p|onion)(:[0-9]+)?$' |
sudo xargs netselect -t$test_time -s$top_n
