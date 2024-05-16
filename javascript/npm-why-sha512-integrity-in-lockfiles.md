https://stackoverflow.com/questions/47638381/why-did-package-lock-json-change-the-integrity-hash-from-sha1-to-sha512

to answer the title question

> why sha512

because "more is better", but [sha256 is not broken](https://crypto.stackexchange.com/questions/47809/why-havent-any-sha-256-collisions-been-found-yet)

because [on 64bit cpus sha512 is faster than sha256](https://crypto.stackexchange.com/questions/26336/sha-512-faster-than-sha-256)

because the npm devs dont see how sha512 is a waste of disk space.  
using truncated sha512 hashes would help:

```
$ printf hello | sha256sum - | cut -f1 -d' ' | xxd -r -p | base64 -w0
LPJNul+wow4m6DsqxbninhsWHlwfp0JecwQzYpOLmCQ=

$ printf hello | sha512sum - | cut -f1 -d' ' | xxd -r -p | base64 -w0 | head -c43
m3HSJL1i83hdltRq0+o9czGb+8KJDKra4t/3JRlnPKc

$ printf hello | sha512sum - | cut -f1 -d' ' | xxd -r -p | base64 -w0
m3HSJL1i83hdltRq0+o9czGb+8KJDKra4t/3JRlnPKcjI8PZm6XBHXx6zG4UuMXaDEZjR1wuXDre9G9zvN7AQw==
```

[Replace SHA1 with SHA512 npm/cli#5920](https://github.com/npm/cli/pull/5920)

> As we know that SHA1 is vulnerable and deprecated, SHA-512 is more realible and secure.

meanwhile, [most git repos are still using sha1](https://stackoverflow.com/questions/28159071/why-doesnt-git-use-more-modern-sha/), [git added support for sha256](https://stackoverflow.com/questions/60087759/git-is-moving-to-new-hashing-algorithm-sha-256-but-why-git-community-settled-on) on 2018-08-04,  
and most other projects ([bitcoin](https://en.bitcoin.it/wiki/SHA-256), [nix](https://discourse.nixos.org/t/why-dont-nix-hashes-use-base-16/11325/12), ...) are using sha256, because [sha256 is not broken](https://crypto.stackexchange.com/questions/47809/why-havent-any-sha-256-collisions-been-found-yet)
