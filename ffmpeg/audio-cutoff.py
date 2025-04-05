#!/usr/bin/env python3

# get the maximum frequency
# of an audio spectrum
# as an indicator
# of the actual audio quality

# generated by deepseek.com

# prompt
"""
create a python script
to detect the maximum frequency 
in an m4a audio file.
that maximum frequency is produced
by the lowpass filter
of the aac audio encoder.
high-quality audio
has a maximum frequency
around 20 KHz (fullband),
low-quality audio
has a maximum frequency
around 3 KHz (narrowband).
use ffmpeg to decode the audio
to pcm
in chunks of 10 seconds.
for each chunk:
detect the local maximum,
print the local maximum
and the chunk time
with the format
f"t={t}sec f={f}KHz",
update the global maximum.
to detect the local maximum,
remove the noise floor
around -110dB,
then find the maximum frequency
in the spectrum.
accept some command line options:
--ss n:
pass as "-ss n" to ffmpeg.
--to n:
pass as "-to n" to ffmpeg.
both -ss and -to args
must come before the -i arg
for ffmpeg input seeking.
print all frequencies in KHz.
add a shebang line before the script,
spaced by an empty line.
---
the script returns 0.24KHz
instead of 19.6KHz.
"""

#!/usr/bin/env python3

import argparse
import numpy as np
import subprocess
import sys

def analyze_audio(input_file, start_time=None, end_time=None):
    cmd = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel', 'error',
    ]
    
    if start_time is not None:
        cmd.extend(['-ss', str(start_time)])
    if end_time is not None:
        cmd.extend(['-to', str(end_time)])
    
    cmd.extend([
        '-i', input_file,
        '-ac', '1',
        '-ar', '44100',
        '-f', 'f32le',
        '-acodec', 'pcm_f32le',
        '-'
    ])
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    chunk_size = 10 * 44100
    bytes_per_sample = 4
    global_max_freq = 0
    current_time = start_time if start_time else 0
    
    while True:
        raw_data = process.stdout.read(chunk_size * bytes_per_sample)
        if not raw_data:
            break
        
        samples = np.frombuffer(raw_data, dtype=np.float32)
        if len(samples) == 0:
            current_time += 10
            continue
        
        # Apply window function
        window = np.hanning(len(samples))
        windowed_samples = samples * window
        
        # Normalized FFT
        fft_result = np.fft.rfft(windowed_samples)
        fft_magnitude = np.abs(fft_result) / len(samples)  # Normalization
        
        # Convert to dBFS
        fft_db = 20 * np.log10(fft_magnitude + 1e-12)
        
        # Remove noise floor
        fft_db_clean = np.where(fft_db > -110, fft_db, -np.inf)
        
        # Find maximum frequency
        max_bin = np.argmax(fft_db_clean)
        max_freq = max_bin * (44100 / 2) / (len(samples) / 2)  # Correct frequency calculation
        
        max_freq_khz = max_freq / 1000
        
        if max_freq_khz > global_max_freq:
            global_max_freq = max_freq_khz
        
        print(f"t={current_time}sec f={max_freq_khz:.2f}KHz")
        current_time += 10
    
    print(f"\nGlobal maximum frequency: {global_max_freq:.2f}KHz")
    
    if global_max_freq > 15:
        print("Quality: Fullband (high quality)")
    elif global_max_freq > 5:
        print("Quality: Wideband (medium quality)")
    else:
        print("Quality: Narrowband (low quality)")

def main():
    parser = argparse.ArgumentParser(description='Detect maximum frequency in an M4A audio file')
    parser.add_argument('input_file', help='Input M4A audio file')
    parser.add_argument('--ss', type=float, help='Start time in seconds')
    parser.add_argument('--to', type=float, help='End time in seconds')
    
    args = parser.parse_args()
    analyze_audio(args.input_file, args.ss, args.to)

if __name__ == '__main__':
    main()
