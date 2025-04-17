import wave
import numpy as np
import os
import pandas as pd
from pydub import AudioSegment

# Folder containing the audio files
folder_path = "plucks"
results = []


def zero_crossings_in_array(arr):
    # Detect zero crossings (crossing from + to - or - to +)
    zero_crossings = []
    for i in range(len(arr - 1)):
        if (arr[i] > 0 and arr[i + 1] < 0) or (arr[i] < 0 and arr[i + 1] > 0):
            zero_crossings.append(i)

    return zero_crossings


# Loop through each WAV file containing "converted" in the filename
for filename in os.listdir(folder_path):
    if "converted" in filename and filename.endswith(".wav"):
        input_path = os.path.join(folder_path, filename)
        filtered_path = "temp_filtered.wav"

        # Extract actual frequency from filename (e.g., "pluck_cropped_82.4Hz_converted.wav")
        try:
            freq_part = filename.split("_")[2]  # e.g., "82.4Hz"
            true_freq = float(freq_part.replace("Hz", ""))
        except:
            true_freq = None

        # Load original for unfiltered zero crossing
        with wave.open(input_path, "r") as song_wav:
            raw_bytes = song_wav.readframes(-1)
            sample_rate = song_wav.getframerate()
            duration = song_wav.getnframes() / sample_rate
        raw = np.frombuffer(raw_bytes, dtype=np.int16)
        raw = raw / np.max(np.abs(raw))  # Normalize
        zc_raw = sum((raw[:-1] > 0) & (raw[1:] < 0) | (raw[:-1] < 0) & (raw[1:] > 0))  # Count zero crossings
        freq_zc = (zc_raw / duration) / 2

        # Apply low-pass filter using PyDub
        song = AudioSegment.from_wav(input_path)
        filtered = song.low_pass_filter(500)
        filtered.export(filtered_path, format="wav")

        # Zero crossing after filtering
        with wave.open(filtered_path, "r") as song_wav:
            raw_bytes_filt = song_wav.readframes(-1)
            sample_rate_filt = song_wav.getframerate()
            duration_filt = song_wav.getnframes() / sample_rate_filt
        raw_filt = np.frombuffer(raw_bytes_filt, dtype=np.int16)
        raw_filt = raw_filt / np.max(np.abs(raw_filt))
        zc_filt = sum((raw_filt[:-1] > 0) & (raw_filt[1:] < 0) | (raw_filt[:-1] < 0) & (raw_filt[1:] > 0))  # Count zero crossings
        freq_zc_filt = (zc_filt / duration_filt) / 2

        # Store result
        results.append({
            "Filename": filename,
            "Frequency (Hz)": true_freq,
            "Frequency (estimated by ZC) (Hz)": round(freq_zc, 2),
            "Frequency (estimated by ZC + low pass at 500Hz) (Hz)": round(freq_zc_filt, 2),
            "Audio duration (s)": round(duration, 4)
        })

# Save results to Excel
df = pd.DataFrame(results)
df.to_excel("tables\\zero_crossings_auto_generated_table.xlsx", index=False)

print("✅ Table saved as 'zero_crossings_auto_generated_table.xlsx'")
