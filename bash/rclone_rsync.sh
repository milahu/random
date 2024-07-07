#!/usr/bin/env bash

set -eux



function rclone_rsync() {

  # rsync-like wrapper for rclone

  # use rclone as a drop-in replacement for rsync
  # note: some rsync options are not supported: -r, -a, ...

  # https://rclone.org/sftp/
  # https://github.com/rclone/rclone/issues/7935
  # https://forum.rclone.org/t/get-rid-of-rsync-replace-it-by-rclone-for-remote-backups/8949/2
  # https://forum.rclone.org/t/rsync-equivalent/37348/2

  local src=""
  local dst=""
  # TODO switch subcommand based on args: sync | copy
  local subcmd=sync
  local args=()

  # parse args
  while [ $# != 0 ]; do case "$1" in
    # this works for joined args like "--transfers=8"
    # but fails for splitted args like "--transfers 8"
    # TODO better ...
    # https://github.com/milahu/parse-helptext
    -*)
      args+=("$1")
      shift
      continue
    ;;
    *)
      if [ -z "$src" ] || [ -z "$dst" ]; then
        local loc="$1" # location
        shift
        local ssh_remote="${loc%:*}"
        local loc_rest="${loc##*:}"

        if [ "$ssh_remote" != "$loc" ] && [ -n "$ssh_remote" ]; then
          echo "found ssh_remote ${ssh_remote@Q} with loc_rest ${loc_rest@Q}" # debug
          # get ssh config
          while IFS=" " read -r key val; do
            eval "local $key=${val@Q}"
          done < <(
            ssh -G "$ssh_remote"
          )
          # translate location from ssh to rclone
          loc="$host"
          loc+=,type=sftp
          loc+=,host="$hostname"
          loc+=,port="$port"
          loc+=,user="$user"
          loc+=,key_file="$identityfile"
          # todo more
          # pubkey_file=
          # key_use_agent=true # use ssh-agent
          # use_insecure_cipher=true
          # known_hosts_file=~/.ssh/known_hosts
          # shell_type=unix
          # md5sum_command=md5sum
          # sha1sum_command=sha1sum
          # set_env="A=1 B=2"
          # ciphers="aes128-ctr aes192-ctr"
          # socks_proxy=myUser:myPass@localhost:9005

          loc+=":$loc_rest"
        fi

        if [ -z "$src" ]; then src="$loc"; continue
        elif [ -z "$dst" ]; then dst="$loc"; continue
        fi
      else
        echo "error: unrecognized argument: ${1@Q}"
        return 1
      fi
    ;;
  esac; done

  # --config /dev/null is needed
  # so rclone does not add this config to ~/.config/rclone/rclone.conf

  rclone \
    --config /dev/null \
    $subcmd \
    "${args[@]}" \
    "$src" \
    "$dst"
}



if false; then
  # example use
  if false; then
    rsync -raPv somedir/ example.com:somedir/
  else
    rclone_rsync -Pv somedir/ example.com:somedir/
  fi
fi
