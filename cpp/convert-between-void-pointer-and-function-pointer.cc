/*

  https://stackoverflow.com/a/78334741/10440128

  https://stackoverflow.com/questions/1096341/function-pointers-casting-in-c

  I have a void pointer returned by dlsym(),
  I want to call the function pointed by the void pointer.
  So I do a type conversion by casting:

    void *gptr = dlsym(some symbol..) ;
    typedef void (*fptr)();
    fptr my_fptr = static_cast<fptr>(gptr) ;

  I have also tried reinterpret_cast but no luck,
  although the C cast operator seems to work..

*/

#include <stdio.h>
//#include <cstdint> // uintptr_t

int fn(int x) {
  return x + 1;
}

int main() {

  void *void_ptr = (void*)&fn;

  typedef int (*fn_ptr_t)(int);

#ifndef __cplusplus
  // C
  fn_ptr_t fn_ptr = NULL;
#else
  // C++
  fn_ptr_t fn_ptr = nullptr;
#endif

#ifndef __cplusplus
  // C
  // this just works in C
  fn_ptr = void_ptr;
#else
  // C++
  // error: invalid conversion from ‘void*’ to ‘fn_ptr_t’ {aka ‘int (*)(int)’}
  //fn_ptr = void_ptr;

  // this works, but its verbose
  //fn_ptr = reinterpret_cast<fn_ptr_t>(reinterpret_cast<uintptr_t>(void_ptr));

  // cast with typeof. im surprised that C++ does not do this automatically
  fn_ptr = (typeof(fn_ptr))(void_ptr);
#endif

  // should return 2
  return fn_ptr(1);
}
