"""
check if a stat object is readable or writable

useful to check if a pipe is readable or writable

probably breaks on windows

https://stackoverflow.com/questions/2113427/determining-whether-a-directory-is-writeable/72803873#72803873
"""

import os, stat

def check_access(s, check="r"):
  "check if s=os.stat(path) is readable or writable"
  u = os.geteuid(); g = os.getegid(); m = s.st_mode
  if check == "r":
    return (
      ((s[stat.ST_UID] == u) and (m & stat.S_IRUSR)) or
      ((s[stat.ST_GID] == g) and (m & stat.S_IRGRP)) or
      (m & stat.S_IROTH)
    ) != 0
  if check == "w":
    return (
      ((s[stat.ST_UID] == u) and (m & stat.S_IWUSR)) or
      ((s[stat.ST_GID] == g) and (m & stat.S_IWGRP)) or
      (m & stat.S_IWOTH)
    ) != 0

s = os.stat(0) # fd 0 == stdin
print(f"fd 0 is readable?", check_access(s, "r"))

s = os.stat(1) # fd 1 == stdout
print(f"fd 1 is writable?", check_access(s, "w"))

os.write(1, b"hello\n")
