#!/usr/bin/env bash

# Python's os.path.join function in Bash
#
# it should be implemented as a pure Bash function
# with zero dependencies on external tools like sed
#
# on error, the function should return 1
# but it should not print an error message

if true; then
# bash.path.join(){
function join_paths() {
    # Bash version of Python's os.path.join function
    # https://docs.python.org/3.9/library/os.path.html#os.path.join
    # https://stackoverflow.com/a/79778845/10440128
    [ $# = 0 ] && return 1
    local a=("$@") s=${a[-1]} i
    for (( i=$#-2; i>=0; --i )); do
        [[ $s = /* ]] && break
        s=${a[i]%/}${a[i]:+/}$s
    done
    printf '%s' "$s" # echo would break on s="-n"
}
fi

if false; then
# if true; then
function join_paths() {
    # Bash version of Python's os.path.join function
    # https://docs.python.org/3.9/library/os.path.html#os.path.join
    # https://stackoverflow.com/a/79778816/10440128
    # con: this requires "sed"
    # note: this collapses more multiple slashes than Python's os.path.join
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
fi

if false; then
# if true; then
# path_join() {
function join_paths() {
    # Bash version of Python's os.path.join function
    # https://docs.python.org/3.9/library/os.path.html#os.path.join
    # https://stackoverflow.com/a/79779437/10440128
    # Python's version requires at least one argument (even an empty string will do)
    if [[ $# -eq 0 ]]; then
        echo "error: at least one path segment required" 2>&1
        return 1
    fi

    local -a segments=()
    local last_seg='' seg

    # Build up an array of segments from which to build the final path
    # The array is cleared before adding a segment starting with a '/'
    # Up to one trailing '/' is removed from each segment (after evaluating
    #   the previous considerations)
    for seg; do
        case $seg in
            '') ;;
            /*) segments=("${seg%/}") ;;
            *) segments+=("${seg%/}") ;;
        esac
        last_seg=$seg
    done

    # If the original form of the last accepted segment ended with a '/' or if
    # the last segment was empty then cause a trailing slash to be (re)introduced
    # by adding an empty segment
    if [[ -z "$last_seg" ]] || [[ "$last_seg" =~ .*/$ ]]; then
        segments+=('')
    fi

    # Join the segments with '/' characters and emit the result
    local IFS='/'
    printf '%s' "${segments[*]}"
}
fi

if false; then
# if true; then
# the worst possible solution... but useful for testing
# https://stackoverflow.com/a/79778844/10440128
# function pyjoin(){ python -c 'import os, sys; print(os.path.join(*sys.argv[1:]))' "$@"; }
function join_paths(){ python -c 'import os, sys; print(os.path.join(*sys.argv[1:]))' "$@" 2>/dev/null; }
fi

# test
function test_join_paths() {
    expected_rc="$1"
    expected="$2"
    shift 2
    # https://stackoverflow.com/a/79778844/10440128
    # expected="$(python -c 'import os, sys; print(os.path.join(*sys.argv[1:]))' "$@" 2>/dev/null)"; expected_rc=$?
    actual="$(join_paths "$@" 2>&1)"
    actual_rc=$?
    if [ "$expected" != "$actual" ] || [ "$expected_rc" != "$actual_rc" ]; then
        echo -n "FIXME test_join_paths"
        for a in "$expected" "$@"; do printf " %q" "$a"; done
        echo " # actual: ${actual@Q} # expected_rc: $expected_rc # actual_rc: $actual_rc"
    fi
}
test_join_paths 1 ""
test_join_paths 0 "" ''
test_join_paths 0 "" '' ''
test_join_paths 0 "a/b/c" a b c
test_join_paths 0 "a/b/c/" a/ b/ c/
test_join_paths 0 "a//b//c//" a// b// c//
test_join_paths 0 "a///b///c///" a/// b/// c///
test_join_paths 0 "a/b/../c" a b ../c
test_join_paths 0 "/c" a b /c
test_join_paths 0 "//c" a b //c
test_join_paths 0 "////c" a b ////c
test_join_paths 0 "a/b/c" a b '' c
test_join_paths 0 "////c/" a b ////c ''
test_join_paths 0 "a a a/b b/c" 'a a a' 'b b' c
test_join_paths 0 $'a\na/b\tb/c\rc' $'a\na' $'b\tb' $'c\rc'
test_join_paths 0 "a/b//c/d" a b//c d
test_join_paths 0 "-n" '-n'
