import wave
import numpy as np
import os
import pandas as pd
from pydub import AudioSegment

# Path to the folder containing audio clips of plucked sounds
folder_path = "plucks"

# We'll collect results in this list, each entry will become a row in our final Excel table
results = []

# --- Utility function ---
def zero_crossings_in_array(arr):
    """
    Detects zero-crossings in a 1D array of audio amplitude values.
    A zero-crossing is counted when the waveform transitions from positive to negative or vice versa.
    """
    zero_crossings = []
    for i in range(len(arr - 1)):
        if (arr[i] > 0 and arr[i + 1] < 0) or (arr[i] < 0 and arr[i + 1] > 0):
            zero_crossings.append(i)
    return zero_crossings


# --- Main Processing Loop ---
# We go through every file in the folder that includes "converted" in its name
for filename in os.listdir(folder_path):
    if "converted" in filename and filename.endswith(".wav"):
        input_path = os.path.join(folder_path, filename)
        filtered_path = "temp_filtered.wav"  # Temporary output after low-pass filtering

        # Attempt to extract the "true" frequency embedded in the filename
        # For example: "pluck_cropped_82.4Hz_converted.wav" -> 82.4
        try:
            freq_part = filename.split("_")[2]  # Assumes filename format is consistent
            true_freq = float(freq_part.replace("Hz", ""))
        except:
            true_freq = None  # Fallback if parsing fails

        # --- Analyze original audio for zero-crossings ---
        with wave.open(input_path, "r") as song_wav:
            raw_bytes = song_wav.readframes(-1)  # Read all frame data
            sample_rate = song_wav.getframerate()
            duration = song_wav.getnframes() / sample_rate  # Duration in seconds

        # Convert audio bytes to 16-bit numpy array and normalize amplitude
        raw = np.frombuffer(raw_bytes, dtype=np.int16)
        raw = raw / np.max(np.abs(raw))

        # Count zero crossings in the raw (unfiltered) signal
        zc_raw = sum((raw[:-1] > 0) & (raw[1:] < 0) | (raw[:-1] < 0) & (raw[1:] > 0))
        freq_zc = (zc_raw / duration) / 2  # Basic frequency estimation via zero-crossing count

        # --- Apply a low-pass filter to clean up the signal ---
        song = AudioSegment.from_wav(input_path)
        filtered = song.low_pass_filter(500)
        filtered.export(filtered_path, format="wav")  # Save to temporary file

        # Analyze the filtered audio for zero-crossings
        with wave.open(filtered_path, "r") as song_wav:
            raw_bytes_filt = song_wav.readframes(-1)
            sample_rate_filt = song_wav.getframerate()
            duration_filt = song_wav.getnframes() / sample_rate_filt

        # Convert filtered audio to array and normalize
        raw_filt = np.frombuffer(raw_bytes_filt, dtype=np.int16)
        raw_filt = raw_filt / np.max(np.abs(raw_filt))

        # Count zero crossings in the filtered signal
        zc_filt = sum((raw_filt[:-1] > 0) & (raw_filt[1:] < 0) | (raw_filt[:-1] < 0) & (raw_filt[1:] > 0))
        freq_zc_filt = (zc_filt / duration_filt) / 2

        # --- Store results for this file ---
        results.append({
            "Filename": filename,
            "Frequency (Hz)": true_freq,
            "Frequency (estimated by ZC) (Hz)": round(freq_zc, 2),
            "Frequency (estimated by ZC + low pass at 500Hz) (Hz)": round(freq_zc_filt, 2),
            "Audio duration (s)": round(duration, 4)
        })

# --- Export all results as an Excel spreadsheet ---
df = pd.DataFrame(results)
df.to_excel("tables\\zero_crossings_auto_generated_table.xlsx", index=False)

print("✅ Table saved as 'zero_crossings_auto_generated_table.xlsx'")
