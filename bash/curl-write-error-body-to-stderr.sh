#!/usr/bin/env bash

# https://superuser.com/a/1834410/951886
# Can I make cURL fail with an exitCode different than 0 if the HTTP status code is not 200?

# to also write the error body to stderr,
# parse the response headers in bash,
# and then, depending on the response status,
# send the response body to stdout (cat) or to stderr (cat >&2)

curl -s --fail-with-body -D - -o - https://httpbin.dev/status/418 | {
  status=
  while read -r header; do
    header="${header:0: -1}" # strip trailing "\r"
    #echo "header: ${header@Q}" >&2 # debug
    if [ -z "$status" ]; then
      status=${header#* } # first header has status
      status=${status%% *}
      continue
    fi
    [ -z "$header" ] && break # end of headers
  done
  #echo "status: $status" >&2 # debug
  if [ "${status:0:1}" = 2 ]; then
    cat # write body to stdout
  else
    cat >&2 # write body to stderr
  fi
} |
cat >/dev/null

# this should write "I'm a teapot!" to stderr
