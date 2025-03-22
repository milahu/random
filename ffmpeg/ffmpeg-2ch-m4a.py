#!/usr/bin/env python3

import subprocess
import sys
import json
import re
import time
from math import sqrt

# Function to get audio channel layout
def get_audio_channel_layout(video_file, audio_stream_index=0):
    command = [
        'ffprobe', '-v', 'error',
        '-select_streams', f'a:{audio_stream_index}',
        '-show_entries', 'stream=channel_layout',
        '-of', 'json', video_file
    ]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"ffprobe error: {result.stderr}")
        data = json.loads(result.stdout)
        if 'streams' in data and len(data['streams']) > 0:
            return data['streams'][0].get('channel_layout', None)
        else:
            raise Exception("No audio stream found.")
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to generate downmix coefficients
def get_coefficients_for_downmix_to_stereo(input_channel_layout):
    if input_channel_layout in ("mono", "1ch", "1.0", "stereo", "2ch", "2.0"):
        return None  # No downmix needed

    if input_channel_layout in ("5.1", "5.1(side)", "6ch"):
        front = 1
        center = (1 / sqrt(2))
        side1 = (sqrt(3) / 2)
        side2 = (1 / 2)
        lfe = (1 / sqrt(2))
        n = 2 / (front + center + side1 + side2 + lfe)
        return {
            "FL": {"FL": front * n, "FC": center * n, "FR": 0, "BL": side1 * n, "BR": side2 * n, "LFE": lfe * n},
            "FR": {"FL": 0, "FC": center * n, "FR": front * n, "BL": side2 * n, "BR": side1 * n, "LFE": lfe * n},
        }

    return None  # Unsupported layout

# Function to generate FFmpeg pan filter for downmixing
def get_ffmpeg_audio_filter_for_downmix_to_stereo(input_channel_layout):
    coefficients = get_coefficients_for_downmix_to_stereo(input_channel_layout)
    if coefficients is None:
        return None
    return "pan=stereo|" + "|".join(
        f"{ch}=" + "+".join(f"{coef}*{src}" for src, coef in mapping.items())
        for ch, mapping in coefficients.items()
    )

# Function to generate loudnorm filter
def get_loudnorm_filter(loudnorm_json):
    measured_I = loudnorm_json["input_i"]
    measured_TP = loudnorm_json["input_tp"]
    measured_LRA = loudnorm_json["input_lra"]
    measured_thresh = loudnorm_json["input_thresh"]
    measured_offset = loudnorm_json["target_offset"]

    if -25 <= measured_I <= -21:
        print(f"Loudness is within acceptable range ({measured_I} dB), skipping normalization.")
        return None

    print(f"Applying loudnorm: I={measured_I}, TP={measured_TP}, LRA={measured_LRA}, Thresh={measured_thresh}")
    return (f"loudnorm=I=-23:TP=-1.5:LRA=11:"
            f"measured_I={measured_I}:measured_TP={measured_TP}:"
            f"measured_LRA={measured_LRA}:measured_thresh={measured_thresh}:"
            f"offset={measured_offset}:linear=true:print_format=none")

# Function to determine the FFmpeg audio filter chain
def get_audio_filter_chain(input_channel_layout, loudnorm_json=None):
    filters = []

    # Add downmix filter if needed
    downmix_filter = get_ffmpeg_audio_filter_for_downmix_to_stereo(input_channel_layout)
    if downmix_filter:
        filters.append(downmix_filter)

    # Add loudnorm filter if needed
    if loudnorm_json:
        loudnorm_filter = get_loudnorm_filter(loudnorm_json)
        if loudnorm_filter:
            filters.append(loudnorm_filter)

    return ",".join(filters) if filters else None

# Function to process the video file
def process_video_file(input_file, audio_stream_index=0):
    output_file = f"{input_file}.2ch.m4a"

    # Get audio channel layout
    acl = get_audio_channel_layout(input_file, audio_stream_index)
    if not acl:
        print("Could not determine audio layout. Skipping file.")
        return

    # ** First pass: Get loudness stats **
    first_pass_command = [
        'ffmpeg', '-hide_banner', '-nostdin', '-i', input_file,
        '-af', f"loudnorm=I=-23:TP=-1.5:LRA=11:print_format=json",
        '-f', 'null', '-'
    ]

    print("Running first pass (analyzing loudness)...")
    result = subprocess.run(first_pass_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Extract JSON from stderr
    json_match = re.search(r'(\{(?:.|\n)*\})', result.stderr)
    if json_match:
        try:
            loudnorm_json = json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return
    else:
        print("Failed to extract loudnorm statistics.")
        return

    # Generate the final audio filter chain
    audio_filter_chain = get_audio_filter_chain(acl, loudnorm_json)

    # Skip second pass if no processing is needed
    if not audio_filter_chain:
        print("No processing needed. Audio is already at the correct loudness and stereo format.")
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

    print("Running second pass (applying normalization if necessary)...")
    subprocess.run(second_pass_command, check=True)
    print(f"Processing complete. Output file: {output_file}")

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        process_video_file(filename)
