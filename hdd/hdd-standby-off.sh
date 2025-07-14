#!/bin/sh
# force hard drives to keep running by reading random blocks
# aka: disable standby for hard drives to increase the service life
# max($RANDOM) == 32767; 32768 * 4096 = 128 MByte
# iflag=direct: bypass the kernel cache
# https://unix.stackexchange.com/a/797933/295986
while true; do
  date -Is
  for dev in /dev/sd?; do
    # echo dev=$dev
    dd if=$dev iflag=direct bs=4096 skip=$RANDOM count=1 status=none of=/dev/null
  done
  sleep 1m
done
