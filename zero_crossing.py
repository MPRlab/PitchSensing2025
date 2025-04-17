import wave
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import os

# Folder containing the audio files
folder_path = "plucks"

# Loop through each file in the folder
for filename in os.listdir(folder_path):
    if "converted" in filename and filename.endswith(".wav"):
        input_file = os.path.join(folder_path, filename)
        filtered_file = "temp_filtered.wav"  # Temporary filtered output

        print(f"\nProcessing: {filename}")

        # Load the audio file and apply low-pass filter
        song = AudioSegment.from_wav(input_file)
        filtered = song.low_pass_filter(500)  # Low-pass cutoff at 500 Hz
        filtered.export(filtered_file, format="wav")  # Save filtered audio

        # Open filtered audio with wave module
        with wave.open(filtered_file, "r") as song_wav:
            raw_bytes = song_wav.readframes(-1)
            sample_rate = song_wav.getframerate()
            duration = song_wav.getnframes() / sample_rate

        # Convert raw bytes to numpy array (assumes 16-bit mono audio)
        raw = np.frombuffer(raw_bytes, dtype=np.int16)

        # Normalize amplitude
        raw = raw / np.max(np.abs(raw))

        # Detect zero crossings (crossing from + to - or - to +)
        zero_crossings = []
        for i in range(len(raw) - 1):
            if (raw[i] > 0 and raw[i + 1] < 0) or (raw[i] < 0 and raw[i + 1] > 0):
                zero_crossings.append(i)

        # Estimate frequency using zero crossing rate
        estimated_frequency = (len(zero_crossings) / duration) / 2

        # Output results
        print(f"Number of Zero Crossings: {len(zero_crossings)}")
        print(f"Duration: {duration:.4f} s")
        print(f"Estimated Frequency: {estimated_frequency:.2f} Hz")

        # Plot the waveform and highlight zero crossings
        """
        plt.figure(figsize=(12, 4))
        plt.plot(raw, label="Waveform", color="blue", alpha=0.7)
        plt.scatter(zero_crossings, raw[zero_crossings], color="red", label="Zero Crossings", s=10)
        plt.title(f"Zero Crossings: {filename}")
        plt.xlabel("Sample Index")
        plt.ylabel("Amplitude")
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.show()
        """
