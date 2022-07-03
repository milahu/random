# javascript read with timeout

[fs.readSync](https://nodejs.org/api/fs.html#fsreadsyncfd-buffer-offset-length-position) with timeout, using [child_process.spawnSync](https://nodejs.org/api/child_process.html#child_processspawnsynccommand-args-options) to call [dd](https://man.archlinux.org/man/dd.1)

calling `dd` (RSS 0.5 MB) is cheaper than calling `node` (RSS 40 MB)

unix only. on windows this may work with `busybox dd`

see also [How to timeout an fs.read in node.js? at stackoverflow.com](https://stackoverflow.com/questions/20808126/how-to-timeout-an-fs-read-in-node-js)

## output

```
$ make -j3

node readWithTimeout.js
read ok
'+'
node readWithTimeout.js
read ok
'+'
node readWithTimeout.js
read error: timeout
node readWithTimeout.js
read error: timeout
make: INTERNAL: Exiting with 1 jobserver tokens available; should be 3!
```

`+node` tells make to run node with make jobserver

make says "should be 3" because we did not write the tokens back to the jobserver on fd 4

this is part of my [gnumake-tokenpool for javascript](https://github.com/milahu/gnumake-tokenpool/tree/main/js)

based on the answer by verybadalloc
