import wave
import numpy as np
import os
import pandas as pd
from pydub import AudioSegment

# Path to the folder containing pluck audio samples
folder_path = "plucks"

# Final data will be stored here before being written to Excel
results = []

# --- Utility function ---
def zero_crossings_in_array(arr):
    """
    Counts zero-crossings in a 1D waveform array (amplitude values).
    A zero-crossing occurs when the waveform moves from positive to negative or vice versa.
    """
    zero_crossings = []
    for i in range(len(arr) - 1):
        if (arr[i] > 0 and arr[i + 1] < 0) or (arr[i] < 0 and arr[i + 1] > 0):
            zero_crossings.append(i)
    return zero_crossings

# --- Main processing loop ---
# Iterate through all WAV files that include "converted" in their filename
for filename in os.listdir(folder_path):
    if "converted" in filename and filename.endswith(".wav"):
        input_path = os.path.join(folder_path, filename)
        filtered_path = "temp_filtered.wav"  # Temporary output path for filtered audio

        # Extract the true frequency from the filename (e.g. "pluck_cropped_82.4Hz_converted.wav")
        try:
            freq_part = filename.split("_")[2]  # Pull out "82.4Hz"
            true_freq = float(freq_part.replace("Hz", ""))  # Convert to float
        except:
            true_freq = None  # Leave as None if parsing fails

        # --- Analyze the original (unfiltered) audio ---
        with wave.open(input_path, "r") as song_wav:
            raw_bytes = song_wav.readframes(-1)  # Read all samples
            sample_rate = song_wav.getframerate()
            duration = song_wav.getnframes() / sample_rate  # Duration in seconds

        raw = np.frombuffer(raw_bytes, dtype=np.int16)  # Convert bytes to waveform
        raw = raw / np.max(np.abs(raw))  # Normalize

        # Use the utility function to count zero-crossings
        zc_raw = len(zero_crossings_in_array(raw))
        freq_zc = (zc_raw / duration) / 2  # Estimate frequency

        # --- Low-pass filter the audio to isolate dominant frequency content ---
        song = AudioSegment.from_wav(input_path)
        filtered = song.low_pass_filter(500)
        filtered.export(filtered_path, format="wav")

        # Load and analyze the filtered audio
        with wave.open(filtered_path, "r") as song_wav:
            raw_bytes_filt = song_wav.readframes(-1)
            sample_rate_filt = song_wav.getframerate()
            duration_filt = song_wav.getnframes() / sample_rate_filt

        raw_filt = np.frombuffer(raw_bytes_filt, dtype=np.int16)
        raw_filt = raw_filt / np.max(np.abs(raw_filt))  # Normalize

        zc_filt = len(zero_crossings_in_array(raw_filt))
        freq_zc_filt = (zc_filt / duration_filt) / 2  # Estimate freq from filtered waveform

        # --- Save this file's analysis as a row in the results table ---
        results.append({
            "Filename": filename,
            "Frequency (Hz)": true_freq,
            "Frequency (estimated by ZC) (Hz)": round(freq_zc, 2),
            "Frequency (estimated by ZC + low pass at 500Hz) (Hz)": round(freq_zc_filt, 2),
            "Audio duration (s)": round(duration, 4)
        })

# --- Write everything to a spreadsheet ---
df = pd.DataFrame(results)
df.to_excel("tables\\zero_crossings_auto_generated_table.xlsx", index=False)

print("Table saved as 'zero_crossings_auto_generated_table.xlsx'")
