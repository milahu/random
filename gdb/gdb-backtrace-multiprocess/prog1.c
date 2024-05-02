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
  printf("prog1: calling prog2\n");
  int res;
  res = execvp("./prog2", argv);
  //res = execlp("./prog2", "asdf", (char *)NULL);
  if (res != 0) {
    fatal_error("prog1: error\n");
  }
  return 0;
}
