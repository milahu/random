#!/usr/bin/env bash

cat >/dev/null <<'EOF'

  create a chain of programs
  prog1 calls prog2
  prog2 calls prog3
  prog3 calls prog4
  ...

  the last program fails to call the next program

  i want to use gdb to trace the instructions
  before the last program crashes with fatal_error
  but gdb fails to catch "exit" in the last program

  ./make.sh && ./prog1

  ./make.sh && ./gdb.sh

EOF

num_progs=2

for i in $(seq $num_progs); do

next=$((i + 1))

cat >prog$i.c <<EOF
#include <stdlib.h> // exit
#include <stdarg.h> // va_end
#include <stdio.h> // print
#include <unistd.h> // exec

// wine/dlls/ntdll/unix/server.c
static void fatal_error( const char *err, ... )
{
    va_list args;

    va_start( args, err );
    //fprintf( stderr, "wine: " );
    fprintf( stderr, "fatal_error: " );
    vfprintf( stderr, err, args );
    va_end( args );
    exit(1);
}

int main(int argc, char **argv) {
  printf("prog$i: calling prog$next\n");
  int res;
  res = execvp("./prog$next", argv);
  //res = execlp("./prog$next", "asdf", (char *)NULL);
  if (res != 0) {
    fatal_error("prog$i: error\n");
  }
  return 0;
}
EOF

gcc -o prog$i prog$i.c

done
