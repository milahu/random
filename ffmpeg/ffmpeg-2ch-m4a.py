#!/usr/bin/env python3

import subprocess
import sys
import json
import re
import argparse
from math import sqrt

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Two-pass volume normalization with optional downmixing for stereo output.")
    parser.add_argument("input_files", nargs="+", help="Input video files.")
    parser.add_argument("-a", "--audio-stream", type=int, default=0, help="Specify the audio stream index (default: 0).")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode for detailed logs.")
    parser.add_argument("--slow", action="store_true", help="Limit FFmpeg to 1 CPU core for lower system load.")
    return parser.parse_args()

# Function to get audio channel layout
def get_audio_channel_layout(video_file, audio_stream_index=0):
    command = [
        'ffprobe', '-v', 'error',
        '-select_streams', f'a:{audio_stream_index}',
        '-show_entries', 'stream=channel_layout',
        '-of', 'json', video_file
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        data = json.loads(result.stdout)
        return data['streams'][0].get('channel_layout', None) if 'streams' in data and data['streams'] else None
    except Exception:
        return None

# Function to generate loudnorm filter
def get_loudnorm_filter(loudnorm_json):
    measured_I = loudnorm_json["input_i"]

    if -25 <= measured_I <= -21:
        return None  # Skip normalization if within acceptable range

    return (f"loudnorm=I=-23:TP=-1.5:LRA=11:"
            f"measured_I={measured_I}:measured_TP={loudnorm_json['input_tp']}:"
            f"measured_LRA={loudnorm_json['input_lra']}:measured_thresh={loudnorm_json['input_thresh']}:"
            f"offset={loudnorm_json['target_offset']}:linear=true:print_format=none")

# Function to determine the FFmpeg audio filter chain
def get_audio_filter_chain(input_channel_layout, loudnorm_json=None):
    filters = []

    if input_channel_layout not in ("mono", "1ch", "1.0", "stereo", "2ch", "2.0"):
        filters.append("pan=stereo|FL=0.5*FL+0.5*FR|FR=0.5*FL+0.5*FR")

    if loudnorm_json:
        loudnorm_filter = get_loudnorm_filter(loudnorm_json)
        if loudnorm_filter:
            filters.append(loudnorm_filter)

    return ",".join(filters) if filters else None

# Function to process the video file
def process_video_file(input_file, audio_stream_index=0, debug=False, slow=False):
    output_file = f"{input_file}.2ch.m4a"

    # Get audio channel layout
    acl = get_audio_channel_layout(input_file, audio_stream_index)
    if not acl:
        print(f"Error: Could not determine audio layout for {input_file}. Skipping.")
        return

    # ** First pass: Get loudness stats **
    first_pass_command = [
        'ffmpeg', '-hide_banner', '-nostdin', '-i', input_file,
        '-af', "loudnorm=I=-23:TP=-1.5:LRA=11:print_format=json",
        '-f', 'null', '-'
    ]
    if slow:
        first_pass_command.extend(['-threads', '1', '-filter_threads', '1'])
    if debug:
        print(f"Running first pass: {' '.join(first_pass_command)}")

    result = subprocess.run(first_pass_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Extract JSON from stderr
    json_match = re.search(r'(\{(?:.|\n)*\})', result.stderr)
    if json_match:
        try:
            loudnorm_json = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            print(f"Error: JSON decode failed for {input_file}. Skipping.")
            return
    else:
        print(f"Error: Failed to extract loudnorm statistics for {input_file}. Skipping.")
        return

    # Generate the final audio filter chain
    audio_filter_chain = get_audio_filter_chain(acl, loudnorm_json)

    # Skip second pass if no processing is needed
    if not audio_filter_chain:
        print(f"Skipping {input_file}: Audio is already at correct loudness and stereo format.")
        return

    # ** Second pass: Apply normalization if needed **
    second_pass_command = [
        'ffmpeg', '-hide_banner', '-nostdin', '-i', input_file,
        '-c:a', 'aac',
        '-map', f'0:a:{audio_stream_index}',
        '-map_metadata', '0',
        '-movflags', 'faststart',
        '-af', audio_filter_chain,
        '-y', output_file
    ]
    if slow:
        second_pass_command.extend(['-threads', '1', '-filter_threads', '1'])
    if debug:
        print(f"Running second pass: {' '.join(second_pass_command)}")

    subprocess.run(second_pass_command, check=True)
    print(f"Processing complete: {output_file}")

if __name__ == "__main__":
    args = parse_arguments()
    for filename in args.input_files:
        process_video_file(filename, audio_stream_index=args.audio_stream, debug=args.debug, slow=args.slow)
