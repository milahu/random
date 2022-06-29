/*
check if a stat object is readable or writable

useful to check if a pipe is readable or writable

probably breaks on windows

https://stackoverflow.com/questions/2113427/determining-whether-a-directory-is-writeable/72803873#72803873
*/

const fs = require('fs');
const os = require('os');

function checkAccess(s, check="r") {
  // check if s=fs.statSync(path) is readable or writable
  const { uid: u, gid: g } = os.userInfo();
  const m = s.mode;
  if (check == "r") {
    return (
      ((s.uid == u) && (m & fs.constants.S_IRUSR)) ||
      ((s.gid == g) && (m & fs.constants.S_IRGRP)) ||
      (m & fs.constants.S_IROTH)
    ) != 0;
  }
  if (check == "w") {
    return (
      ((s.uid == u) && (m & fs.constants.S_IWUSR)) ||
      ((s.gid == g) && (m & fs.constants.S_IWGRP)) ||
      (m & fs.constants.S_IWOTH)
    ) != 0;
  }
  throw Exception("check must be r or w");
}

var s = fs.fstatSync(0); // fd 0 == stdin
console.log("fd 0 is readable?", checkAccess(s, "r"));

var s = fs.fstatSync(1); // fd 1 == stdout
console.log("fd 1 is writable?", checkAccess(s, "w"));

fs.writeSync(1, "hello\n");
