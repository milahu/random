#!/usr/bin/env bash

# remark
ignore_regex="^(glamoroustoolkit.out|remarkable.*-toolchain.out|digitalbitbox.out) "

echo reading lib filenames from stdin
regex='/lib/('
libs=()
while IFS= read -r line; do
  if [ "${line:0:49}" = 'error: auto-patchelf could not satisfy dependency' ]; then
    # parse output from autoPatchelf
    lib=$(echo "${line:50}" | cut -d" " -f1)
  else
    lib="$line"
  fi
  regex+="$lib|"
  libs+=("$lib")
done
regex="${regex:0: -1})"

res=$(nix-locate --top-level --whole-name --at-root --regex "$regex" | grep -v -E "$ignore_regex")



# unpin version if the exact version is not found
# examples:
# libboost_chrono.so.1.71.0
# libprotobuf.so.17
# libssl.so.1.1
# libsodium.so.23

missing_libs=()

for lib in "${libs[@]}"; do
  if echo "res" | grep -q -m1 "/lib/$lib"; then continue; fi
  missing_libs+=("$lib")
done

libs=("${missing_libs[@]}")

regex='/lib/('
for lib in "${libs[@]}"; do
  # TODO incremental: remove only the last ".[0-9]+" suffix
  lib=${lib%.so*}.so
  regex+="$lib|"
done
regex="${regex:0: -1})"

res+=$(nix-locate --top-level --whole-name --at-root --regex "$regex" | grep -v -E "$ignore_regex")



# TODO print nix package with library filename
# example: boost # libboost_chrono.so libboost_filesystem.so libboost_program_options.so libboost_regex.so libboost_serialization.so libboost_thread.so

#echo "$res" | sed -u -E 's/^([^ ]+) .*$/\1/; s/\.out$//' | uniq | sort

declare -A pkg_libs
while IFS= read -r line; do
  #sed -u -E 's/^([^ ]+) .*$/\1/; s/\.out$//' | uniq | sort
  pkg=$(echo "$line" | awk '{ print $1 }')
  pkg=${pkg%.out}
  # default output is openssl.bin
  if [ "$pkg" = "openssl" ]; then
    pkg+=".out"
  fi
  lib=$(echo "$line" | awk '{ print $4 }')
  lib=${lib##*/}
  pkg_libs[$pkg]+=" $lib"
done <<< "$res"
#done < <(echo "$res")

# sort by libs
for pkg in ${!pkg_libs[@]}; do
  libs="${pkg_libs[$pkg]}"
  echo "$pkg #$libs"
done | sort -k3
