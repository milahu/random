#!/usr/bin/env python3

# generated by deepseek.com
# prompts:
"""
show me a python script
that takes an m4a file
(with aac audio)
and detects
the audio encoder's
lowpass filter
"cutoff frequency" in khz,
for example 20 khz
for high-quality audio,
or 10 khz for low-quality audio
"""
"""
please make matplotlib
write the debug plot
to a png file at
f"{input_file_path}.debug-spectrum.png".
also please avoid
creating a temporary wav file,
and try to use ffmpeg
to write wav data to stdout,
and feed that wav data
to wavfile and numpy.
generally,
try to use a streaming algorithm
to reduce memory usage.
"""
"""
no, this still runs out of memory at
```py
stdout_data, stderr_data = proc.communicate()
```
please use a loop to read
chunks of wav data from ffmpeg
and process each chunk separately.
feel free to use
a different format than wav
to make the code easier.
"""
"""
for debugging, print the
intermediate cutoff_khz result
with every loop iteration.
increase the buffer size
to make the loop run
at a lower frequency.
"""
"""
something is wrong here.
the script keeps printing 0 khz
but it should be about 19.6 khz
pretty much from the start
in my example.
"""

#!/usr/bin/env python3

# detect_lowpass.py

import numpy as np
from scipy import signal
import subprocess
import sys
import matplotlib.pyplot as plt

def stream_audio_analysis(m4a_file_path, plot_path=None):
    """Process audio in chunks using ffmpeg stdout streaming"""
    # FFmpeg command for raw PCM output
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', m4a_file_path,
        '-ac', '1',          # mono
        '-ar', '44100',      # sample rate
        '-f', 's16le',       # 16-bit little-endian PCM
        '-'                   # output to stdout
    ]

    # Start ffmpeg process
    proc = subprocess.Popen(ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=10**8,
    )

    # Audio processing parameters
    sample_rate = 44100
    chunk_duration = 10  # seconds per chunk
    chunk_size = sample_rate * chunk_duration
    bytes_per_sample = 2  # 16-bit = 2 bytes
    fft_sum = None
    total_chunks = 0
    frequencies = None
    
    try:
        while True:
            # Read raw PCM bytes in chunks
            raw_bytes = proc.stdout.read(chunk_size * bytes_per_sample)
            if not raw_bytes:
                break

            # Convert bytes to numpy array
            chunk = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32)
            chunk /= 32768.0  # Normalize to [-1, 1]

            # Skip silent chunks
            if np.max(np.abs(chunk)) < 0.001:
                continue

            # Apply window and compute FFT with proper scaling
            window = signal.windows.hann(len(chunk))
            windowed = chunk * window
            fft_result = np.fft.rfft(windowed) * 2 / np.sum(window)  # Window compensation
            
            fft_mag = np.abs(fft_result)
            fft_power = fft_mag ** 2  # Use power spectrum instead of magnitude

            if fft_sum is None:
                fft_sum = fft_power
                frequencies = np.fft.rfftfreq(len(chunk), d=1.0/sample_rate)
            else:
                fft_sum += fft_power
            total_chunks += 1

            # Calculate intermediate results using power spectrum
            current_avg = fft_sum / total_chunks
            current_db = 10 * np.log10(current_avg + 1e-10)  # Power to dB
            
            # Find peak in high-frequency range (1kHz-20kHz)
            hf_mask = (frequencies >= 1000) & (frequencies <= 20000)
            if not np.any(hf_mask):
                continue
                
            peak_db = np.max(current_db[hf_mask])
            target_db = peak_db - 3  # -3dB from HF peak
            
            # Find highest frequency above target
            above_threshold = np.where(current_db >= target_db)[0]
            valid_above = above_threshold[above_threshold <= np.max(np.where(hf_mask)[0])]
            
            if len(valid_above) > 0:
                cutoff_freq = frequencies[valid_above[-1]]
            else:
                cutoff_freq = frequencies[np.max(np.where(hf_mask)[0])]
            
            cutoff_khz = round(cutoff_freq / 500) * 0.5
            
            # Print intermediate results
            print(f"Chunk {total_chunks}: Cutoff estimate: {cutoff_khz:.1f} kHz "
                  f"(Peak: {peak_db:.1f} dB @ {frequencies[np.argmax(current_db[hf_mask]) + np.where(hf_mask)[0][0]]:.0f} Hz)")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except:
            pass

    # Final calculation
    if fft_sum is None:
        raise ValueError("No valid audio data processed")
    
    fft_avg = fft_sum / total_chunks
    fft_db = 10 * np.log10(fft_avg + 1e-10)
    
    # Find final cutoff frequency
    hf_mask = (frequencies >= 1000) & (frequencies <= 20000)
    peak_db = np.max(fft_db[hf_mask])
    target_db = peak_db - 3
    above_threshold = np.where(fft_db >= target_db)[0]
    valid_above = above_threshold[above_threshold <= np.max(np.where(hf_mask)[0])]
    
    if len(valid_above) > 0:
        cutoff_freq = frequencies[valid_above[-1]]
    else:
        cutoff_freq = frequencies[np.max(np.where(hf_mask)[0])]
    
    cutoff_khz = round(cutoff_freq / 500) * 0.5
    
    # Save plot if requested
    if plot_path:
        plt.figure(figsize=(10, 4))
        plt.semilogx(frequencies, fft_db)
        plt.axvline(x=cutoff_freq, color='r', linestyle='--', 
                   label=f'Final cutoff: {cutoff_khz:.1f} kHz')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power (dB)')
        plt.title('Frequency Spectrum Analysis')
        plt.legend()
        plt.grid(True)
        plt.savefig(plot_path)
        plt.close()
    
    return cutoff_khz

def detect_lowpass_cutoff(m4a_file_path):
    """Main detection function"""
    plot_path = f"{m4a_file_path}.debug-spectrum.png"
    return stream_audio_analysis(m4a_file_path, plot_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python detect_lowpass.py <input.m4a>")
        sys.exit(1)
    
    try:
        cutoff = detect_lowpass_cutoff(sys.argv[1])
        print(f"\nFinal estimated lowpass cutoff frequency: {cutoff:.1f} kHz")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
