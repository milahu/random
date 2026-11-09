# Generate EPUB Script

**User:** Anonymous  
**Created:** 2026/11/9 9:35:57  
**Updated:** 2026/11/9 9:38:42  
**Exported:** 2026/11/9 9:40:06  
**Link:** [<https://chatgpt.com/c/6af185ec-d690-83eb-afea-71773461a7c5>](https://chatgpt.com/c/6af185ec-d690-83eb-afea-71773461a7c5)

## Prompt:

11/9/2026, 9:38:09 AM

generate a python script to create an EPUB file from the files in the workdir.

for this task, currently i am using this bash script:

``` bash
#!/usr/bin/env bash

epub="$1"

if false; then
  echo "error: missing argment: epub"
  echo "hint: $0 path/to/output-file.epub"
  exit 1
fi

if [ -z "$epub" ]; then
  # default: write to out.epub in workdir
  epub="out.epub"
fi

if [ -e "$epub" ]; then
  echo "error: output file exists: $epub"
  exit 1
fi

# get absolute path
epub="$(realpath "$epub")"

src="$2"

if [ -z "$src" ]; then
  # default: use files from workdir
  src="."
fi

cd "$src"

if ! [ -e mimetype ]; then
  echo "error: missing source file: mimetype"
  exit 1
fi

# https://gist.github.com/bryanrieger/622abf99685126b2711b58b36b5ae840
# ePub Shell Commands
# To zip up an epub

# create a new zip archive
# -X: Do not save extra file attributes
zip -X "$epub" mimetype

# grow the zip archive
zip "$epub" . --grow --recurse-paths --exclude mimetype "$epub"

# done
echo "$epub"
```

but the resulting EPUB files are not reproducible, because they contain file times

the python script should add all files to the zip archive in a predictable (reproducible) way, so all file times are set to zero, and it uses the default compression (except for the mimetype file at the start of the archive)

## Response:

11/9/2026, 9:38:11 AM

Here's a Python replacement using only the standard library (`pathlib`, `zipfile`, and `argparse`).

It creates **reproducible EPUB files** by sorting all archive entries, assigning fixed timestamps, and excluding filesystem-dependent metadata.

One important detail: ZIP timestamps cannot represent dates before **1980-01-01**, so that is the earliest portable timestamp, rather than zero.

<CodeBlock language="python" editable>
#!/usr/bin/env python3
"""Create a reproducible EPUB archive from a directory."""

import argparse  
from pathlib import Path  
from zipfile import ZipFile, ZipInfo, ZIP_STORED, ZIP_DEFLATED

TIMESTAMP = (1980, 1, 1, 0, 0, 0)

def create_epub(output: Path, source: Path) -\> None:  
output = output.resolve()  
source = source.resolve()

    mimetype = source / "mimetype"
    if not mimetype.is_file():
        raise FileNotFoundError(f"missing source file: {mimetype}")

    if output.exists():
        raise FileExistsError(f"output file exists: {output}")

    files = sorted(
        (p for p in source.rglob("*") if p.is_file()
         and p.resolve() != output),
        key=lambda p: p.relative_to(source).as_posix(),
    )

    with ZipFile(output, "x", compression=ZIP_DEFLATED) as epub:
        for path in [mimetype, *[p for p in files if p != mimetype]]:
            name = path.relative_to(source).as_posix()

            info = ZipInfo(name, date_time=TIMESTAMP)
            info.compress_type = (
                ZIP_STORED if name == "mimetype" else ZIP_DEFLATED
            )
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits = 0
            info.extra = b""
            info.comment = b""

            epub.writestr(info, path.read_bytes())

    print(output)

def main() -\> None:  
parser = argparse.ArgumentParser(description=**doc**)  
parser.add_argument(  
"epub", nargs="?", default="out.epub",  
type=Path, help="output EPUB file (default: out.epub)"  
)  
parser.add_argument(  
"src", nargs="?", default=".",  
type=Path, help="source directory (default: current directory)"  
)  
args = parser.parse_args()

    create_epub(args.epub, args.src)

if **name** == "**main**":  
main()  
</CodeBlock>

## Usage

Exactly like your Bash script:

## Reproducibility guarantees

| Property               | Behavior                                   |
|------------------------|--------------------------------------------|
| File order             | Sorted lexicographically                   |
| `mimetype`             | Always first                               |
| `mimetype` compression | `ZIP_STORED` (uncompressed)                |
| Other files            | `ZIP_DEFLATED` (default compression level) |
| Timestamps             | Fixed to 1980-01-01 00:00:00               |
| Permissions            | Fixed to `0644`                            |
| File ownership         | Not stored                                 |
| ZIP extra fields       | Empty                                      |
| Directory entries      | Omitted                                    |
| Existing output        | Refused                                    |

The script also ensures that the output EPUB itself isn't accidentally included when writing it into the source directory.

**Note:** Given identical input files, this produces byte-identical EPUBs when using the same Python/zlib environment. Different zlib versions can potentially produce different compressed bytes, even with identical inputs and settings.

The EPUB-specific requirement that `mimetype` be the first entry and uncompressed is satisfied.

------------------------------------------------------------------------

Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)
