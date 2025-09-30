#!/usr/bin/env bash

function join_paths() {
    # Bash version of Python's os.path.join function
    # https://docs.python.org/3.9/library/os.path.html#os.path.join
    # https://stackoverflow.com/a/79778816/10440128
    local result=""
    local arg
    for arg; do
        if [ "${arg:0:1}" = / ]; then
            result="$arg"
            continue
        fi
        if [ -z "$result" ]; then
            result="$arg"
            continue
        fi
        result="$result/$arg"
    done
    # collapse multiple slashes
    # but preserve UNC paths like //hostname/path
    result="$(echo "$result" | sed -E 's#([^/])/{2,}#\1/#g')"
    echo "$result"
}

# test
function test_join_paths() {
    expected="$1"
    shift
    actual=$(join_paths "$@")
    if [ "$expected" != "$actual" ]; then
        echo -n "FIXME test_join_paths"
        for a in "$expected" "$@"; do printf " %q" "$a"; done
        echo " # actual: $actual"
    fi
}
test_join_paths "a/b/c" a b c
test_join_paths "a/b/c/" a/ b/ c/
test_join_paths "a/b/../c" a b ../c
test_join_paths "/c" a b /c
test_join_paths "//c" a b //c
test_join_paths "////c" a b ////c
