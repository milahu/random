# pandoc plain text input

pandoc does not support the input format "plain"

```sh
pandoc -f plain -t html example.txt -o example.html
```

error:

```sh
Unknown input format plain
```

## custom pandoc reader

fix: use a custom pandoc reader: [plain.lua](plain.lua)

```sh
pandoc -f plain.lua -t html example.txt -o example.html
```

https://github.com/jgm/pandoc/issues/6393

https://pandoc.org/custom-readers#example-plain-text-reader
