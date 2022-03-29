#! /usr/bin/env bash

function difflines() {
  # compare files line-by-line
  # https://stackoverflow.com/a/71665866/10440128
  local W=1000 # depends on input width
  local c=$(((W+1)/2)) # center. +1 to round up
  local ca=$((c-1))
  local cb=$((c+3))
  diff -y -t -W $W "$1" "$2" | while read -r L
  do
    a="$(echo "$L" | cut -c1-$ca | sed -E 's/ +$//')"
    b="$(echo "$L" | cut -c$cb-)"
    echo "-$a"
    echo "+$b"
    echo
  done
}

false && cat <<EOF_EOF

example:

```sh
cat >file1 <<EOF
t1 = "Christmas 2013"
t2 = "Easter 2013"
t3 = "Thanksgiving 2013"
EOF

cat >file2 <<EOF
t1 = "Christmas 2014"
t2 = "Easter 2014"
t3 = "Thanksgiving 2014"
EOF

difflines file1 file2
```

output

```txt
-t1 = "Christmas 2013"
+t1 = "Christmas 2014"

-t2 = "Easter 2013"
+t2 = "Easter 2014"

-t3 = "Thanksgiving 2013"
+t3 = "Thanksgiving 2014"
```

EOF_EOF
