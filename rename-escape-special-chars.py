#!/usr/bin/env python3

r'''
https://unix.stackexchange.com/questions/216659
How to rename all files with special characters and spaces in a directory?

https://www.reddit.com/r/linux/comments/otsr4a/whats_your_tool_to_rename_files_in_batch_from/
What's your tool to rename files (in batch) from weird internet filenames to clean [a-zA-Z0-9-_] or similar filenames?

https://github.com/dharple/detox/issues/100
utf_8 filter converts spaces to underscores

https://askubuntu.com/questions/671320
How to rename file names to avoid conflict in Windows or Mac?
'''

import argparse
import os
import re
from pathlib import Path

INVALID_CHARS = r'[<>:"/\\|?*\x00-\x1F]'

RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

MAX_BYTES = 240


def truncate_utf8(name: str, max_bytes: int) -> str:
    encoded = name.encode("utf-8")

    if len(encoded) <= max_bytes:
        return name

    encoded = encoded[:max_bytes]

    while True:
        try:
            return encoded.decode("utf-8")
        except UnicodeDecodeError:
            encoded = encoded[:-1]


def sanitize(name: str) -> str:
    stem, suffix = os.path.splitext(name)

    stem = re.sub(INVALID_CHARS, "_", stem)
    suffix = re.sub(INVALID_CHARS, "_", suffix)

    stem = re.sub(r"_+", "_", stem)
    suffix = re.sub(r"_+", "_", suffix)

    stem = stem.rstrip(" .")
    suffix = suffix.rstrip(" .")

    if not stem:
        stem = "_"

    if stem.upper() in RESERVED:
        stem += "_"

    ext_bytes = len(suffix.encode("utf-8"))
    stem = truncate_utf8(stem, MAX_BYTES - ext_bytes)

    return stem + suffix


def key(name: str) -> str:
    """
    Comparison key for filesystems that are case-insensitive.
    """
    return name.casefold()


def allocate_names(entries):
    """
    Given a list of directory entries, return a mapping:
        old_name -> new_name

    Collisions are detected before any rename happens.
    """

    existing = {key(e.name) for e in entries}

    result = {}
    reserved = set()

    # First reserve names that don't need changing.
    for entry in entries:
        cleaned = sanitize(entry.name)

        if cleaned == entry.name:
            reserved.add(key(cleaned))

    # Then assign changed names.
    for entry in entries:
        old = entry.name
        cleaned = sanitize(old)

        if cleaned == old:
            result[old] = old
            continue

        candidate = cleaned
        base, ext = os.path.splitext(cleaned)

        counter = 1
        while (
            key(candidate) in reserved
            or key(candidate) in existing and key(candidate) != key(old)
            or key(candidate) in result.values()
        ):
            candidate = f"{base}_{counter}{ext}"
            counter += 1

        result[old] = candidate
        reserved.add(key(candidate))

    return result


def rename_directory(directory: str, dry_run=False):
    with os.scandir(directory) as it:
        entries = list(it)

    mapping = allocate_names(entries)

    for old, new in mapping.items():
        if old == new:
            continue

        src = os.path.join(directory, old)
        dst = os.path.join(directory, new)

        print(f"{src!r} -> {dst!r}")

        if not dry_run:
            os.rename(src, dst)


def rename_tree(root: str, dry_run=False):
    for current, dirs, files in os.walk(root, topdown=False):

        # Files and directories share the same namespace on all
        # filesystems we care about, so process them together.
        rename_directory(current, dry_run)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--dry-run", "-n", action="store_true")
    args = parser.parse_args()

    rename_tree(args.directory, args.dry_run)


if __name__ == "__main__":
    main()
