import wave
import numpy as np
import os
import pandas as pd
from pydub import AudioSegment
import math

# Folder containing the input .wav files
folder_path = "plucks"
results = []  # List to store results for each file


def estimate_freq_via_xor_trigger(file_path, num_samples=1000):
    # ==============================================================================
    #  Copyright (c) 2014-2018 Joel de Guzman. All rights reserved.
    #
    #  Distributed under the Boost Software License, Version 1.0. (See accompanying
    #  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
    # ==============================================================================
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

    results_autocorr = []
    leng = math.floor(len(trig) / 2)
    for i in range(leng):
        x = [a ^ b for a, b in zip(trig[0:leng], trig[i:i + leng])]
        results_autocorr.append(count_ones(x))
    results_autocorr.extend(results_autocorr)

    # Find the first notch (minimum) in correlation after skipping initial overlap
    skip = 20
    search_range = results_autocorr[skip:leng]
    if not search_range:
        return 0.0
    notch_index_relative = np.argmin(search_range)
    notch_index = notch_index_relative + skip

    estimated_period = notch_index / framerate
    estimated_frequency = 1 / estimated_period if estimated_period > 0 else 0

    return estimated_frequency


# --- Main processing loop over all WAV files in the folder ---
for filename in os.listdir(folder_path):
    # Only consider real samples (not generated)
    if "converted" in filename and filename.endswith(".wav") and "artificial" not in filename:
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

        # Estimate frequency using XOR autocorrelation method
        freq_xor = estimate_freq_via_xor_trigger(input_path)
        print(freq_xor)


