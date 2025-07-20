#!/bin/sh

function zpool_rename() {
  local oldname="$1"
  local newname="$2"
  zpool list &&
  zpool export "$oldname" &&
  zpool import "$oldname" "$newname" &&
  zpool list
}
