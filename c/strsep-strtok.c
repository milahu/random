//usr/bin/env true && exec tcc -run "$0" "$@"

// ^ shebang of c script
// https://stackoverflow.com/questions/2482348/run-c-or-c-file-as-a-script
// https://stackoverflow.com/questions/584714/is-there-an-interpreter-for-c
// https://stackoverflow.com/questions/69539/have-you-used-any-of-the-c-interpreters-not-compilers

// gcc -o strsep-strtok strsep-strtok.c && ./strsep-strtok

// https://stackoverflow.com/questions/7218625/what-are-the-differences-between-strtok-and-strsep-in-c
// use strtok_s on windows
// use strsep on unix
// dont use strsep_r on unix, because its unsafe, and its banned from the git codebase

#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {

  if (argc != 3) {
    printf("usage: %s delim str\n", argv[0]);
    printf("example: %s :+ a:b+c\n", argv[0]);
    return 1;
  }

  const char *delim = argv[1];
  char *str = argv[2];

  if (delim[0] == '\x00') { printf("error: empty delim\n"); return 1; }
  if (str[0] == '\x00') { printf("error: empty str\n"); return 1; }

  char *token = NULL;

  // https://stackoverflow.com/questions/7218625/what-are-the-differences-between-strtok-and-strsep-in-c
  // note: strtok joins multiple delimiters, strsep does not
  // see also: strsep for windows
  // https://stackoverflow.com/questions/8512958/is-there-a-windows-variant-of-strsep-function
  #if defined(_WIN32) || defined(_WIN64)
  // use strtok_s on windows
  char *next_token = NULL;
  while ((token = strtok_s(str, delim, &next_token))) {
  #else
  // use strsep on unix
  while ((token = strsep(&str, delim))) {
  #endif
    printf("token: %s\n", token);
  }

  return 0;
}
