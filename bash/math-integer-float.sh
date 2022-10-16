#! /bin/sh

# bash: convert between integer and float numbers in pure bash,
# without calling any external binaries, to avoid context switching

# based on https://github.com/tartley/rerun2/pull/12

# run online https://replit.com/@milahu/math-integer-float-sh

for ignore_msecs in "" 0 1 12 123 1234 12345 123456 1234567 12345678 123456789
do

  # int msecs -> float secs
  a=000$ignore_msecs
  a=${a:0: -3}
  while [ "${a:0:1}" = 0 ]; do a=${a:1}; done
  if [ -z "$a" ]; then a=0; fi
  b=000$ignore_msecs
  b=${b: -3}
  ignore_secs=$a.$b

  if [[ "$ignore_msecs" == "" ]]
  then
    printf '%-10s %10s\n' "(empty)" $ignore_secs
  else
    printf '%-10s %10s\n' $ignore_msecs $ignore_secs
  fi

done
