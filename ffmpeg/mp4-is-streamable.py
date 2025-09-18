#!/usr/bin/env python3

# mp4-is-streamable.py

# Check if an MP4 file is streamable (faststart enabled).
# A file is streamable if the 'moov' atom appears before 'mdat'.

# https://superuser.com/questions/559372/using-ffmpeg-to-locate-moov-atom

import os
import re
import sys
import subprocess

MAX_HEADER_SIZE = 5 * 1024 * 1024  # 5 MiB
MAX_LINES = 10_000  # only read first 10K lines of ffmpeg output

def check_mp4_is_streamable(filename, max_lines=MAX_LINES, max_header_size=MAX_HEADER_SIZE):
    """
    Returns True if the MP4 file is streamable (moov before mdat), False otherwise.
    """
    proc = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-v", "trace", "-i", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={
            "PATH": os.environ["PATH"],
            "LANG": "C",
        }
    )

    moov_offset = None
    mdat_offset = None

    moov_re = re.compile(rb"type:'moov'.*sz:\s*([0-9]+)\s*([0-9]+)\s*([0-9]+)")
    mdat_re = re.compile(rb"type:'mdat'.*sz:\s*([0-9]+)\s*([0-9]+)\s*([0-9]+)")

    for i, line in enumerate(proc.stdout):
        if i >= max_lines:
            break

        if moov_offset is None:
            if m := moov_re.search(line):
                moov_offset = int(m.group(2))  # start offset of moov atom

        if mdat_offset is None:
            if m := mdat_re.search(line):
                mdat_offset = int(m.group(2))  # start offset of mdat atom

        if moov_offset is not None and mdat_offset is not None:
            break

    proc.terminate()
    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()

    if moov_offset is None:
        is_streamable = False  # no moov atom found
    elif mdat_offset is None:
        # is_streamable = False  # no mdat atom found
        is_streamable = moov_offset <= max_header_size
    else:
        # streamable if moov appears before mdat and is within header size
        is_streamable = moov_offset < mdat_offset and moov_offset <= max_header_size

    if 0:
        # debug
        if not is_streamable:
            print(f"{filename}: moov_offset={moov_offset} mdat_offset={mdat_offset}", file=sys.stderr)

    return is_streamable

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} file.mp4", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]
    if check_mp4_is_streamable(filename):
        print("streamable")
    else:
        print("not streamable")

if __name__ == "__main__":
    main()
