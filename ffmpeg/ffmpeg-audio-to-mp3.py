#!/usr/bin/env python3

import argparse
import secrets
import subprocess
import sys
from pathlib import Path


AUDIO_EXTENSIONS = {
    ".aac",
    ".aiff",
    ".aif",
    ".alac",
    ".ape",
    ".flac",
    ".m4a",
    ".m4b",
    ".mp4",
    ".oga",
    ".ogg",
    ".opus",
    ".wavpack",
    ".wma",
}


def random_output_path(directory: Path) -> Path:
    """Return a random, currently non-existing path in directory."""
    while True:
        name = f".{secrets.token_hex(16)}.mp3"
        path = directory / name
        if not path.exists():
            return path


def convert_file(source: Path) -> bool:
    target = source.with_suffix(".mp3")

    # Never overwrite an existing MP3.
    if target.exists():
        print(f"SKIP (target exists): {source}")
        return False

    temp_path = random_output_path(source.parent)

    try:
        print(f"CONVERT: {source} -> {target}")

        result = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel", "error",
                "-i", str(source),
                "-map_metadata", "0",
                "-vn",
                "-codec:a", "libmp3lame",
                "-q:a", "2",
                "-y",
                str(temp_path),
            ],
            check=False,
        )

        if result.returncode != 0:
            print(f"ERROR: FFmpeg failed: {source}", file=sys.stderr)
            temp_path.unlink(missing_ok=True)
            return False

        if not temp_path.is_file() or temp_path.stat().st_size == 0:
            print(
                f"ERROR: FFmpeg produced an empty output: {source}",
                file=sys.stderr,
            )
            temp_path.unlink(missing_ok=True)
            return False

        # Rename the completed conversion to its final name.
        temp_path.replace(target)

        # Only now destroy the contents of the original.
        source.write_bytes(b"")

        print(f"  -> original emptied: {source}")
        return True

    except Exception as exc:
        print(f"ERROR processing {source}: {exc}", file=sys.stderr)
        temp_path.unlink(missing_ok=True)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recursively convert non-MP3/WAV audio files to MP3."
    )
    parser.add_argument(
        "root_directory",
        type=Path,
        help="Root directory of the mounted music player",
    )
    args = parser.parse_args()

    root = args.root_directory.resolve()

    if not root.is_dir():
        print(f"ERROR: Not a directory: {root}", file=sys.stderr)
        return 1

    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("ERROR: ffmpeg is not installed.", file=sys.stderr)
        return 1

    converted = 0
    skipped = 0

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        extension = path.suffix.lower()

        if extension in {".mp3", ".wav"}:
            continue

        if extension not in AUDIO_EXTENSIONS:
            continue

        if convert_file(path):
            converted += 1
        else:
            skipped += 1

    print()
    print(f"Done. Converted: {converted}, skipped/failed: {skipped}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
