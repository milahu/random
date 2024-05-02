#!/bin/sh

args=(
gdb
--quiet
-ex "set breakpoint pending on"
-ex "break execvp"
-ex "break exit"
-ex "run"

# break at execvp
#-ex "catch syscall exit"
-ex "set follow-exec-mode new"
#-ex "set follow-fork-mode child"
-ex "set disassemble-next-line on"
-ex "break abort"
-ex "break fatal_error"
#-ex "catch syscall exit_group"
#-ex "catch syscall group:process"
#-ex "set detach-on-fork off"
#-ex 'where'
#-ex 'info inferiors'
-ex 'info threads'
-ex 'printf "rdi = %s\n", $rdi' # first argument of execvp
-ex 'c'

# break at execvp
#-ex 'where'
#-ex 'info inferiors'
-ex 'info threads'
-ex 'printf "rdi = %s\n", $rdi' # first argument of execvp
#-ex "catch syscall exit_group"
-ex 'c'

# break at exit
-ex 'bt'
--args ./prog1
)

"${args[@]}"
