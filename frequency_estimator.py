import wave
import numpy as np
import os
import pandas as pd
from pydub import AudioSegment
import math

# Folder containing the input .wav files
folder_path = "plucks"
results = []  # List to store results for each file


# --- Utility functions ---
def zero_crossings_in_array(arr):
    """
    Basic zero-crossing detector (no threshold).
    Counts number of times the signal crosses the zero axis.
    """
    zero_crossings = []
    for i in range(len(arr) - 1):
        if (arr[i] > 0 and arr[i + 1] < 0) or (arr[i] < 0 and arr[i + 1] > 0):
            zero_crossings.append(i)
    return zero_crossings


def zero_crossings_in_array_filtered(arr):
    """
    Zero-crossing detector with a dead zone (+/- 0.05).
    Helps avoid counting noise as crossings.
    """
    zero_crossings = []
    for i in range(len(arr) - 1):
        if (arr[i] > 0.05 and arr[i + 1] < -0.05) or (arr[i] < -0.05 and arr[i + 1] > 0.05):
            zero_crossings.append(i)
    return zero_crossings


def estimate_freq_via_xor_trigger(file_path, num_samples=1000):
    """
    Estimates frequency using a binary trigger and XOR autocorrelation on the first few samples.
    Returns estimated frequency in Hz.
    """
    with wave.open(file_path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    dtype = np.int16 if sampwidth == 2 else np.uint8
    raw_audio = np.frombuffer(raw_bytes, dtype=dtype)

    if n_channels > 1:
        raw_audio = raw_audio[::n_channels]

    raw_audio = raw_audio[:num_samples]
    audio = raw_audio / np.max(np.abs(raw_audio))

    # Binary trigger
    class zero_cross:
        def __init__(self):
            self.y = 0

        def __call__(self, s):
            if s < -0.1:
                self.y = 0
            elif s > 0.1:
                self.y = 1
            return self.y

    zc = zero_cross()
    trig = [zc(s) for s in audio]

    # XOR autocorrelation
    def count_ones(l):
        return sum(1 for e in l if e)

    results = []
    leng = math.floor(len(trig) / 2)
    for i in range(leng):
        x = [a ^ b for a, b in zip(trig[0:leng], trig[i:i + leng])]
        results.append(count_ones(x))
    results.extend(results)

    # Find the first notch (minimum) in correlation after skipping initial overlap
    skip = 20
    search_range = results[skip:leng]
    if not search_range:
        return 0.0
    notch_index_relative = np.argmin(search_range)
    notch_index = notch_index_relative + skip

    estimated_period = notch_index / framerate
    estimated_frequency = 1 / estimated_period if estimated_period > 0 else 0

    return estimated_frequency


# --- Main processing loop over all WAV files in the folder ---
for filename in os.listdir(folder_path):
    if "converted" in filename and filename.endswith(".wav"):
        input_path = os.path.join(folder_path, filename)
        filtered_path = "temp_filtered.wav"  # Temporary file for low-pass filtered audio

        # Extract true frequency from filename, e.g. "pluck_cropped_98Hz_converted.wav"
        try:
            freq_part = filename.split("_")[2]
            true_freq = float(freq_part.replace("Hz", ""))
        except:
            true_freq = None

        # --- Load original (unfiltered) audio ---
        with wave.open(input_path, "r") as song_wav:
            raw_bytes = song_wav.readframes(-1)
            sample_rate = song_wav.getframerate()
            duration = song_wav.getnframes() / sample_rate

        # Convert audio bytes to numpy array and normalize
        raw = np.frombuffer(raw_bytes, dtype=np.int16)
        raw = raw / np.max(np.abs(raw))  # Normalize to [-1, 1]

        # Estimate frequency using zero-crossing count
        zc_raw = len(zero_crossings_in_array(raw))
        freq_zc = (zc_raw / duration) / 2  # Divide by 2 because each full wave has two crossings

        # --- Apply low-pass filter using PyDub (cutoff = 500Hz) ---
        song = AudioSegment.from_wav(input_path)
        filtered = song.low_pass_filter(500)  # Simple LPF
        filtered.export(filtered_path, format="wav")  # Export to temporary file

        # Load filtered audio
        with wave.open(filtered_path, "r") as song_wav:
            raw_bytes_filt = song_wav.readframes(-1)
            sample_rate_filt = song_wav.getframerate()
            duration_filt = song_wav.getnframes() / sample_rate_filt

        # Convert filtered audio bytes to array and normalize
        raw_filt = np.frombuffer(raw_bytes_filt, dtype=np.int16)
        raw_filt = raw_filt / np.max(np.abs(raw_filt))

        # Estimate frequency again using zero-crossings on filtered audio
        zc_filt = len(zero_crossings_in_array(raw_filt))
        freq_zc_filt = (zc_filt / duration_filt) / 2

        # Estimate frequency using XOR autocorrelation method
        freq_xor = estimate_freq_via_xor_trigger(input_path)

        # Save results for this file
        results.append({
            "Filename": filename,
            "Frequency (Hz)": true_freq,
            "Frequency (estimated by ZC) (Hz)": round(freq_zc, 2),
            "Frequency (estimated by ZC + LPF 500Hz) (Hz)": round(freq_zc_filt, 2),
            "Frequency (estimated by XOR autocorr) (Hz)": round(freq_xor, 2),
            "Audio duration (s)": round(duration, 4)
        })

# --- Export all results to Excel ---
df = pd.DataFrame(results)
df.to_excel("tables\\zero_crossings_auto_generated_table.xlsx", index=False)
print("Table saved as 'zero_crossings_auto_generated_table.xlsx'")
