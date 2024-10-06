#!/bin/sh

# whatismyip.sh
# get my public IP address from a STUN server

# check dependencies
for cmd in timeout stunclient; do
  if command -v $cmd &>/dev/null; then continue; fi
  echo "error: missing command: $cmd" >&2
  exit 1
done

if false; then
  # find nearby STUN servers
  serverlist_url=https://github.com/pradt2/always-online-stun/raw/master/valid_ipv4s.txt
  sudo netselect -s 50 -t 10 $(curl -s -L $serverlist_url) |
  awk '{ print $2 }' |
  xargs sudo netselect -s 10 -t 100 |
  awk '{ print $2 }'
fi

function get_public_ipaddr() {
  # get my public IP address from a STUN server
  # based on https://askubuntu.com/a/683488/877276
  # TODO update the server list for your location
  local stun_server_list="5.9.87.18:3478 74.125.250.129:19302 212.18.0.14:3478 109.68.96.189:3478"
  local stun_server=
  local host=
  local port=
  local res=
  local addr=
  for stun_server in $stun_server_list; do
    IFS=: read host port <<<"$stun_server"
    res="$(
      # fast response: 0.05 seconds
      # slow response: 5 seconds
      #time \
      timeout 0.2 \
      stunclient $host $port
    )"
    if [ $? = 0 ]; then
      # get the "Mapped address"
      addr=$(echo "$res" | tail -n1)
      addr=${addr:16}
      addr=${addr%:*}
      echo $addr
      return
    #else echo "server failed: $stun_server" >&2 # debug
    fi
  done
  return 1 # all servers failed
}

set -e
get_public_ipaddr
