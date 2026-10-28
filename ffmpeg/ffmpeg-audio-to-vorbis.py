#!/usr/bin/env python3

# convert all unsupported (and uncompressed) audio formats to Ogg Vorbis



# https://geizhals.de/agptek-a02-8gb-schwarz-a1406764.html
# Audioformate: AAC, APE, FLAC, MP3, OGG/​Vorbis, WAV, WMA



import argparse
import secrets
import subprocess
import sys
from pathlib import Path


AUDIO_EXTENSIONS = {
    # ".aac",
    ".aiff",
    ".aif",
    ".alac", # TODO convert to FLAC
    # ".ape",
    # ".flac",
    # ".m4a",
    # ".m4b",
    # ".mp4",
    # ".oga",
    # ".ogg",
    ".opus",
    ".wavpack", # TODO convert to FLAC
    ".wma", # TODO convert to FLAC
    # TODO convert more formats? .mka?
}


def random_output_path(directory: Path) -> Path:
    """Return a random, currently non-existing path in directory."""
    while True:
        # name = f".{secrets.token_hex(16)}.mp3"
        name = f".{secrets.token_hex(16)}.ogg"
        path = directory / name
        if not path.exists():
            return path


def convert_file(source: Path) -> bool:
    # target = source.with_suffix(".mp3")
    target = source.with_suffix(".ogg")

    # Never overwrite an existing file.
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
                # "-codec:a", "libmp3lame",

                # https://trac.ffmpeg.org/wiki/Encode/HighQualityAudio
                #
                # Based on quality produced from high to low:
                # "libopus" ≈ "libvorbis" >= "libfdk_aac" > "libmp3lame" >= "eac3"/"ac3" > "aac" > "libtwolame" > "vorbis" > "mp2" > "wmav2"/"wmav1"
                #
                # "libvorbis" - Usable range ≥ 96 Kbps. Recommended range ≥ 192 Kbps.
                #
                # It is not recommended to use the experimental "vorbis" for encoding; use "libvorbis" instead.
                "-codec:a", "libvorbis",
                # https://trac.ffmpeg.org/wiki/TheoraVorbisEncodingGuide
                # -qscale:a – audio quality.
                # Range is -1.0 to 10.0, where 10.0 is highest quality.
                # Default is -q:a 3 with a target of ​112kbps.
                # The formula 16×(q+4) is used below 4, 32×q is used below 8, and 64×(q-4) otherwise.
                # Examples: 112=16×(3+4), 160=32×5, 200=32×6.25, 384=64×(10-4).
                # "-q:a", "-1", # 16*(q+4) = 48 kbps
                # "-q:a", "0", # 16*(q+4) = 64 kbps
                # "-q:a", "1", # 16*(q+4) = 80 kbps
                # "-q:a", "2", # 16*(q+4) = 96 kbps
                # "-q:a", "3", # 16*(q+4) = 112 kbps
                # "-q:a", "4", # 32*q = 128 kbps
                # "-q:a", "5", # 32*q = 160 kbps
                "-q:a", "6", # 32*q = 192 kbps
                # "-q:a", "7", # 32*q = 224 kbps
                # "-q:a", "8", # 64*(q-4) = 256 kbps
                # "-q:a", "9", # 64*(q-4) = 320 kbps
                # "-q:a", "10", # 64*(q-4) = 384 kbps

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
        description="Recursively convert unsupported audio files to Ogg-Vorbis."
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

        # if extension in {".mp3", ".wav"}:
        #     continue

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
