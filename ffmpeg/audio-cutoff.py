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
around -97dB,
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
add a shebang line before the script.
---
the script returns 0.22KHz
instead of 19.6KHz.
---
the script returns 22.05KHz
instead of 19.6KHz.
"""

#!/usr/bin/env python3

import argparse
import numpy as np
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(description='Detect AAC encoder lowpass cutoff frequency')
    parser.add_argument('input_file', help='Input M4A audio file')
    parser.add_argument('--ss', type=float, help='Start time in seconds')
    parser.add_argument('--to', type=float, help='End time in seconds')
    return parser.parse_args()

def find_lowpass_cutoff(fft_db, freqs, sample_rate):
    """Find the AAC encoder's lowpass cutoff frequency"""
    # Typical AAC encoder leaves a drop of ~3dB at the cutoff point
    max_db = np.max(fft_db)
    cutoff_threshold = max_db - 3  # 3dB drop from peak
    
    # Find all frequencies above threshold
    above_threshold = fft_db >= cutoff_threshold
    if not np.any(above_threshold):
        return 0
    
    # The cutoff is the highest frequency with energy above threshold
    return np.max(freqs[above_threshold])

def analyze_chunk(audio_data, sample_rate):
    # Convert to numpy array and normalize
    audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
    
    # Apply window function
    window = np.hanning(len(audio_array))
    audio_windowed = audio_array * window
    
    # Perform FFT
    fft_result = np.fft.rfft(audio_windowed)
    fft_magnitude = np.abs(fft_result)
    fft_db = 20 * np.log10(fft_magnitude + 1e-12)
    freqs = np.fft.rfftfreq(len(audio_array), d=1.0/sample_rate)
    
    # Find the lowpass cutoff frequency
    cutoff_freq = find_lowpass_cutoff(fft_db, freqs, sample_rate)
    return cutoff_freq / 1000  # Convert to kHz

def main():
    args = parse_args()
    
    # Configure FFmpeg command
    ffmpeg_cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error']
    if args.ss: ffmpeg_cmd.extend(['-ss', str(args.ss)])
    if args.to: ffmpeg_cmd.extend(['-to', str(args.to)])
    
    ffmpeg_cmd.extend([
        '-i', args.input_file,
        '-f', 's16le', '-ac', '1', '-ar', '48000',  # Higher sample rate helps
        '-acodec', 'pcm_s16le', '-'
    ])
    
    chunk_duration = 10  # seconds
    sample_rate = 48000
    chunk_size = sample_rate * chunk_duration * 2  # 2 bytes per sample
    
    print(f"Analyzing {args.input_file} for AAC lowpass cutoff...")
    
    global_max = 0
    with subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE) as proc:
        for chunk_num in range(1000):  # Safety limit
            audio_data = proc.stdout.read(chunk_size)
            if not audio_data or len(audio_data) < chunk_size:
                break
            
            cutoff = analyze_chunk(audio_data, sample_rate)
            t = chunk_num * chunk_duration
            print(f"t={t}sec f={cutoff:.2f}KHz")
            
            if cutoff > global_max:
                global_max = cutoff
    
    print(f"\nDetected AAC lowpass cutoff: {global_max:.2f}KHz")
    
    # Quality classification
    if global_max > 19: print("Quality: Fullband (high quality)")
    elif global_max > 15: print("Quality: Wideband (good quality)")
    elif global_max > 10: print("Quality: Medium band")
    elif global_max > 5: print("Quality: Narrowband")
    else: print("Quality: Very narrowband (low quality)")

if __name__ == '__main__':
    main()
