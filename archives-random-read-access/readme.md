https://github.com/yarnpkg/berry/discussions/6297

> Allowing them to use a different format(zip) which is better for their global cache.

why repack from tgz to zip?

why is zip better than tgz?

i only heard the rumor of "fast random read access"
but in my simple benchmark, `tar xf` is 5x faster than `unzip` 

```
unzip    0.266s
tar xf   0.041s
sqlite   0.050s
```

npm is based on tgz, git is based on gzip, ...
zstd would give better performance

> sha-512

sha512 is a waste of disk space, because [sha256 is not broken](https://crypto.stackexchange.com/questions/47809/why-havent-any-sha-256-collisions-been-found-yet)
but thats a separate issue, which also affects `npm`
