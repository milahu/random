https://stackoverflow.com/questions/50069235/what-are-all-of-the-file-extensions-supported-by-ffmpeg

in python, this is trivial with [pyav](https://github.com/PyAV-Org/PyAV)

> `python -c 'import av; print("\n".join([ formats + ":" + ",".join(extensions) for formats, extensions in (map(lambda format: (format, list(av.format.ContainerFormat(format).extensions)), av.formats_available))]))'`

```
binka:binka
adp:adp,dtk
ilbc:lbc
sol:
fwse:fwse
s24be:
xvag:xvag
avif:avif
redspark:rsd
msf:msf
...
```

note: formats can have multiple names:

```
mov,mp4,m4a,3gp,3g2,mj2:mp4,mov,3gp,psp,isma,3g2,ismv,f4v,avif,m4b,mj2,m4a,ism
```

see also `formats_available` and `ContainerFormat` in [av/format.pyx](https://github.com/PyAV-Org/PyAV/blob/main/av/format.pyx)

> JavaFX

in java, you will need to find a way to call `libavformat.so`

see also [Where to get full list of libav* formats?](https://stackoverflow.com/questions/2940521/where-to-get-full-list-of-libav-formats)
