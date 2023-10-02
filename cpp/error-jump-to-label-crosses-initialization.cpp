int main() {
  goto some_label;

  // error: jump to label ‘some_label’ crosses initialization of ‘int x’
  //int x = 1; // error

  // ok: split the initialization in two
  // https://stackoverflow.com/a/24015044/10440128
  int x;
  x = 1;

  some_label:
  return x;
}
