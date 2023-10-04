#! /usr/bin/env bash

# refactor C++ code
# split variable declaration and initialization
# as a workaround for "crosses initialization" errors
# when porting code from C to C++
# because this is no error in C code

# example diff:
# - int a = 1;
# + int a;
# + a = 1;

# usage:
# - set the source path
# - maybe set CXXFLAGS
# - run this script. this will:
#   - call "make"
#   - parse the output of "g++"
#   - write "todo.diff"
# - apply the patch with "patch -p1 <todo.diff"
#   - in rare cases, some diff hunks will fail to apply
#     so you have to manually patch the code
# - retry to compile = manually run "make"
# - maybe repeat, until all "crosses initialization" errors are gone

# TODO support multiple source paths

# TODO implement this with a proper C++ refactoring tool based on clang
# https://clang.llvm.org/docs/RefactoringEngine.html



source_path="main.cpp"

CXXFLAGS=""
# -fpermissive = allow some errors
# -w = hide all warnings
# -I = add an include path
#CXXFLAGS="-fpermissive -w -I/nix/store/q6l92a4rgqr8sfccssh8nzc6amkdnzdv-wine-8.10/include/wine/msvcrt"



{

  jump_error=false

  added_lines=0

  done_init_line_numbers=""

  # output the diff header
  echo "--- a/$source_path"
  echo "+++ b/$source_path"

  while IFS= read -r init_line
  do

    init_line_number=$(echo "$init_line" | grep -o -E '^[0-9]+')
    echo "init_line_number: $init_line_number" >&2
    init_line_source="$(echo "$init_line" | sed -E 's/^[0-9]+ \| //')"
    echo "init_line_source: '$init_line_source'" >&2

    if [[ " $done_init_line_numbers " =~ " $init_line_number " ]]; then
      # already done this line
      # dont repeat the diff block
      echo "ignoring duplicate error" >&2
      #jump_error=false
      continue
    fi

    # example:
    # init_line_source: '    int32_t v294 = v125; // 0x404c14'

    # remove right side of assignment
    # a: int32_t v294 = v125; // 0x404c14
    # a: int32_t v294; // 0x404c14
    init_part_1="$(echo "$init_line_source" | sed -E 's| = .*;|;|')"
    # remove type before assignment
    # a: int32_t v294 = v125; // 0x404c14
    # b: v294 = v125; // 0x404c14
    init_part_2="$(echo "$init_line_source" | sed -E 's|^( +)([a-zA-Z0-9_]+) |\1|')"

    new_init_line_number=$((init_line_number + added_lines))

    # output a diff block
    echo "@@ -$init_line_number +$new_init_line_number,2 @@"
    echo "-$init_line_source"
    echo "+$init_part_1"
    echo "+$init_part_2"

    added_lines=$((added_lines + 1))
    # no. one "jump error" can have multiple "crosses initialization"
    #jump_error=false
    done_init_line_numbers+=" $init_line_number"

  done < <(

    while IFS= read -r line
    do

      false && echo "line: $line"

      if ! $jump_error && echo "$line" | grep -q -E "^$source_path:[0-9]+:[0-9]+: error: jump to label "
      then
        #echo "found jump to label error" >&2
        jump_error=true
        read
        read
      fi

      if $jump_error
      then
        if echo "$line" | grep -q -E "^$source_path:[0-9]+:[0-9]+: note:   from here$"
        then
          read
          read
        elif echo "$line" | grep -q -E "^$source_path:[0-9]+:[0-9]+: note:   crosses initialization of"
        then
          read init_line
          read
          echo "init line: $init_line" >&2
          echo "$init_line"
        fi
      fi
    done < <(
      make CXXFLAGS="$CXXFLAGS" 2>&1 |
      grep -A999 ': error: jump to label '
    ) |
    sort -n -u
    # to create a valid diff, we have to sort by line number
    # and we need a unique list of lines
  )

} | tee todo.diff

echo done todo.diff
