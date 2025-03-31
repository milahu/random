#!/usr/bin/env python3

# https://superuser.com/questions/1727737
# Accurately extract frames every N seconds

# https://superuser.com/questions/1274661
# Selecting one every n frames from a video using ffmpeg

# https://www.reddit.com/r/ffmpeg/comments/s6gn24/how_to_process_every_nth_frame_of_a_video_without/
# only keyframes
# -skip_frame nokey

import os, sys
import subprocess

# Extract a frame every n seconds
dt = 10

input_file = sys.argv[1]

#dt = int(sys.argv[2])

output_ext = "mp4"
# output_ext = "mkv"



# output_file = f"{input_file}.sync-{dt}s.{output_ext}"

output_file = f"{input_file}.keyframes.{output_ext}"

# select frame every dt seconds
# fixme missing frames
"""
    select='bitor(
    gte(t-prev_selected_t,{dt}),
    isnan(prev_selected_t)
    )',
"""
# https://superuser.com/questions/984686
# Create a image every XX seconds of the video
# select='not(mod(n,{dt}))',

# https://brian.carnell.com/articles/2021/use-ffmpeg-to-extract-an-image-from-a-video-every-n-seconds/
# fps=1/{dt},

# downscale to 720p = 1280x720
# scale=-2:720
# scale=1280:-2
# scale=1280:trunc(ow/a/2)*2
# https://stackoverflow.com/questions/8218363/maintaining-aspect-ratio-with-ffmpeg
w = 1280
# downscale to 360p = 640x360
w = 640
vf = rf"""
    scale={w}:trunc(ow/a/2)*2
"""

# https://gist.github.com/kuntau/a7cbe28df82380fd3467
# yify ffmpeg args
x264_params = ":".join([
    "cabac=1",
    "ref=5",
    "analyse=0x133",
    "me=umh",
    "subme=9",
    "chroma-me=1",
    "deadzone-inter=21",
    "deadzone-intra=11",
    "b-adapt=2",
    "rc-lookahead=60",
    "vbv-maxrate=10000",
    "vbv-bufsize=10000",
    "qpmax=69",
    "bframes=5",
    "b-adapt=2",
    "direct=auto",
    "crf-max=51",
    "weightp=2",
    "merange=24",
    "chroma-qp-offset=-1",
    "sync-lookahead=2",
    "psy-rd=1.00,0.15",
    "trellis=2",
    # place a new keyframe every n frames
    #"min-keyint=23",
    # https://stackoverflow.com/questions/33854390/ffmpeg-how-to-encode-for-seekable-video-at-high-key-frame-interval
    "min-keyint=1",
    "partitions=all",
])

# x264_params = "min-keyint=1"

# x264_params = ""

ffmpeg_cmd = [
    "ffmpeg",
    "-hide_banner",
    "-nostdin",
    "-hwaccel", "auto",
    # only keyframes
    "-skip_frame", "nokey",
    "-i", input_file,
    # debug
    # Limit to first n minutes
    #"-to", "5:00",
    "-vf", vf,
    "-vsync", "0",
    "-map", "0:v",
    # copy chapters
    "-map_metadata", "0",
    # streamable mp4
    "-movflags", "faststart",
    # yify ffmpeg args
    "-c:v", "libx264",
    "-crf", "27",
    "-x264-params", x264_params,
    # https://gist.github.com/parnexcodes/601df332dd06effea254be38132b9c61#file-rarbg-encoding-settings
    # rarbg ffmpeg args
    #"-pix_fmt", "yuv420p",
    # seekable mp4
    # place a new keyframe every n frames
    #"-x264opts", "keyint=1",
    # Overwrite output
    "-y",
    output_file,
]

# Run the command
subprocess.run(
    ffmpeg_cmd,
    check=True
)
