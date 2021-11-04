#!/bin/sh

false && cat <<EOF

fight club: airplane scene

- are there a lot of these kinds of accidents?
- you wouldn't believe it ...
- which kind of company do you work for?
- a major one ...

https://www.youtube.com/watch?v=SiB8GVMNJkE

EOF



set -e

o=1; if [ ! -e $o.txt ]; then echo "building $o.txt ..."
nix-locate --regex '.+\.so$' >$o.txt
echo "building $o.txt done"; else echo "skip $o.txt"; fi

o=2; i=$(($o - 1)); if [ ! -e $o.txt ]; then echo "building $o.txt ..."
while read line; do
  pkg=${line:0:57}
  path=${line:102}
  pathInPkg=${path#*/}
  echo "$pkg $pathInPkg"
done <$i.txt >$o.txt
echo "building $o.txt done"; else echo "skip $o.txt"; fi

o=3; i=$(($o - 1)); if [ ! -e $o.txt ]; then echo "building $o.txt ..."
while read line; do
  [ "${line:58:4}" = 'lib/' ] && echo "$line"
done <$i.txt >$o.txt
echo "building $o.txt done"; else echo "skip $o.txt"; fi

# remove (...) packages, haskellPackages.
o=4; i=$(($o - 1)); if [ ! -e $o.txt ]; then echo "building $o.txt ..."
grep -v -e '^(' -e '^haskellPackages.' $i.txt >$o.txt
echo "building $o.txt done"; else echo "skip $o.txt"; fi

o=5; i=$(($o - 1)); if [ ! -e $o.txt ]; then echo "building $o.txt ..."
while read line; do
  pathInLib="${line:62}"
  slashes=$(echo "$pathInLib" | tr -c -d /)
  depth=${#slashes}
  echo "${line:0:42} $depth ${line:58}" # assume: files have < 10 GByte
done <$i.txt >$o.txt
echo "building $o.txt done"; else echo "skip $o.txt"; fi

# sort
o=6; i=$(($o - 1)); if [ ! -e $o.txt ]; then echo "building $o.txt ..."
sort <$i.txt >$o.txt
echo "building $o.txt done"; else echo "skip $o.txt"; fi

# find pkgs with no top-level libs
o=7; i=$(($o - 1)); if [ ! -e $o.txt ]; then echo "building $o.txt ..."
lastPrefix=""
printPkg=false
while read line; do
  prefix=${line:0:41}
  if [ "$prefix" != "$lastPrefix" ]; then
    # new package
    firstDepth=${line:43:1}
    if [ "$firstDepth" = '0' ]; then
      printPkg=false
      lastPrefix="$prefix"
      continue
    fi
    printPkg=true
  fi
  $printPkg && echo "$line"
  lastPrefix="$prefix"
done <$i.txt >$o.txt
echo "building $o.txt done"; else echo "skip $o.txt"; fi

o=8; i=$(($o - 1)); if [ ! -e $o.txt ]; then echo "building $o.txt ..."
# exclude private libs
grep -v -E -e ' lib/python[23]\.[0-9]+' -e ' lib/(debug|R|perl5|php|lua|ruby|wine|wine64|libreoffice)/' -e '^(ocamlPackages\.|adoptopenjdk|jdk|jre|jetbrains\.jdk)' <$i.txt >$o.txt
echo "building $o.txt done"; else echo "skip $o.txt"; fi
