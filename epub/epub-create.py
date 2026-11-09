#!/usr/bin/env python3

"""Create a reproducible EPUB archive from a directory."""

import argparse
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_STORED, ZIP_DEFLATED

TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def create_epub(output: Path, source: Path) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
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


if __name__ == "__main__":
    main()
