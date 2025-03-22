#!/usr/bin/env python3

import subprocess
import sys
import os
import time

# Get the script directory
d = os.path.dirname(os.path.realpath(__file__))

# Function to get audio channel layout
def get_audio_channel_layout(file_path):
    get_acl_script = os.path.join(d, 'ffprobe-get-audio-channel-layout.sh')
    result = subprocess.run([get_acl_script, file_path], capture_output=True, text=True)
    return result.stdout.splitlines()[0]

# Function to downmix audio to stereo
def downmix_audio_to_stereo(acl):
    get_af_script = os.path.join(d, 'downmix-audio-to-stereo-rfc7845.py')
    result = subprocess.run([get_af_script, acl], capture_output=True, text=True)
    return result.stdout.strip()

# Loop through input files
for i in sys.argv[1:]:
    o = f"{i}.2ch.mp4"
    
    # Get audio channel layout
    acl = get_audio_channel_layout(i)
    print(f"acl: {acl}")
    time.sleep(1)

    # Downmix to stereo if necessary
    af = ""
    if acl not in ("", "mono", "stereo"):
        af = downmix_audio_to_stereo(acl)
        print(f"af: {af}")
        time.sleep(1)

    # Build the ffmpeg command
    a = [
        'ffmpeg',
        '-hide_banner',
        '-nostdin',
        '-i', i,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-movflags', 'faststart',  # mp4 stream
    ]
    
    if af:
        print("downmixing to stereo")
        a.extend(['-af', af])
    else:
        print("not downmixing to stereo")
    
    a.extend(['-y', o])
    
    # Execute the ffmpeg command
    subprocess.run(a, check=True)
