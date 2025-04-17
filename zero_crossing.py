import wave
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment

# Apply low-pass filter using pydub
input_file = "plucks\\pluck_cropped_110Hz_converted.wav"
filtered_file = "temp_filtered.wav"

# Load and filter
song = AudioSegment.from_wav(input_file)
filtered = song.low_pass_filter(500)  # See https://github.com/jiaaro/pydub/blob/master/pydub/effects.py#L222
filtered.export(filtered_file, format="wav")  # Save to temporary file

# Reopen filtered audio using wave module
song_wav = wave.open(filtered_file, "r")
raw_bytes = song_wav.readframes(-1)

# Convert bytes to numpy array (16-bit audio assumed)
raw = np.frombuffer(raw_bytes, dtype=np.int16)

# Get sample rate and duration
sample_rate = song_wav.getframerate()
duration = song_wav.getnframes() / sample_rate

# Normalize amplitude
raw = raw / np.max(np.abs(raw))

# Detect zero crossings
zero_crossings = []

for i in range(len(raw) - 1):
    if (raw[i] > 0 and raw[i + 1] < 0) or (raw[i] < 0 and raw[i + 1] > 0):
        zero_crossings.append(i)

# Frequency estimate (half of zero-crossing rate)
estimated_frequency = (len(zero_crossings) / duration) / 2

# Output
print(f"Number of Zero Crossings: {len(zero_crossings)}")
print(f"Duration: {duration:.4f} s")
print(f"Estimated Frequency: {estimated_frequency:.2f} Hz")

# Plot
plt.figure(figsize=(12, 4))
plt.plot(raw, label="Waveform", color="blue", alpha=0.7)
plt.scatter(zero_crossings, raw[zero_crossings], color="red", label="Zero Crossings", s=10)
plt.title("Zero Crossings after Low-Pass Filtering")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()
