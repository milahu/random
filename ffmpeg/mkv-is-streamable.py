#!/usr/bin/env python3

# mkv-is-streamable.py

# check if an MKV file is streamable
# streamable = progressive playback
# parse the output of `mkvinfo -v -v src.mkv`
# find the position of the first MKV `Cluster` entry

# also check if an MKV file is seekable via cues
# find the position of the MKV `Cues` entry

# tested with mkvinfo v93.0

# https://stackoverflow.com/a/79768193/10440128

import os
import re
import sys
import subprocess

MAX_LINES = 10_000  # only read first 10K lines

MAX_HEADER_SIZE = 5 * 1024 * 1024 # 5 MiB

def check_streamable(filename, max_lines=MAX_LINES, check_seekable=False):
    """
    Check if an MKV file is progressively streamable and has fast-seek cues.
    Reads mkvinfo output line-by-line and stops once both first Cluster and Cues are found.
    """

    # Spawn mkvinfo process
    proc = subprocess.Popen(
        ["mkvinfo", "-v", "-v", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        # text=True,
        env={
            "PATH": os.environ["PATH"],
            "LANG": "C",
        },
    )

    cluster_offset = None
    cues_offset = None

    cluster_re = re.compile(rb"^\|\+ Cluster at ([0-9]+)")
    cues_re = re.compile(rb"^\|\+ Cues at ([0-9]+)")

    # Read mkvinfo output live
    for i, line in enumerate(proc.stdout):
        # print(f"line {line!r}")
        if i >= max_lines:
            break

        if cluster_offset is None:
            if m := cluster_re.match(line):
                cluster_offset = int(m.group(1).decode("ascii"))

        if check_seekable:
            if cues_offset is None:
                if m := cues_re.match(line):
                    cues_offset = int(m.group(1).decode("ascii"))

            # Stop early if we found both
            if cluster_offset is not None and cues_offset is not None:
                break
        else:
            if cluster_offset is not None:
                break

    # Clean up mkvinfo process
    proc.terminate()
    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()

    return (cluster_offset, cues_offset)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} file.mkv", file=sys.stderr)
        sys.exit(1)

    (cluster_offset, cues_offset) = check_streamable(sys.argv[1])

    if cluster_offset is None or cluster_offset > MAX_HEADER_SIZE:
        print("not streamable")
    else:
        print("streamable")
    sys.exit(0)

    r"""
    # Report results
    if cluster_offset is None:
        print("❌ No Cluster element found → invalid MKV?")
        return

    print(f"First Cluster offset: {cluster_offset} bytes")
    if cluster_offset <= MAX_HEADER_SIZE:
        print(f"✅ Cluster appears within {MAX_HEADER_SIZE} bytes → progressively streamable")
    else:
        print(f"⚠️ Cluster appears after {MAX_HEADER_SIZE} bytes → may not be streamable")

    if cues_offset is None:
        print("⚠️ No Cues element found → seeking may be slow")
    else:
        print(f"Cues offset: {cues_offset} bytes")
        if cues_offset <= cluster_offset:
            print("✅ Cues appear before Cluster → fast seeking possible")
        else:
            print("⚠️ Cues appear after Cluster → seeking will require full file scan")
    """

if __name__ == "__main__":
    main()
