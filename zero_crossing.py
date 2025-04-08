import wave
import numpy as np
import matplotlib.pyplot as plt

# Load WAV file
song_file = "C:\\Users\\79140\\Downloads\\pluck_cropped.wav"
song = wave.open(song_file, "r")

# Read audio frames
raw_bytes = song.readframes(-1)

# Convert bytes to NumPy array (adjust dtype if needed — try int16 or int32 based on file)
raw = np.frombuffer(raw_bytes, dtype=np.int16)  # Try int32 if this looks weird

# Get sample rate and duration
sample_rate = song.getframerate()
duration = song.getnframes() / sample_rate

# Normalize amplitude to [-1, 1]
raw = raw / np.max(np.abs(raw))

# Detect zero crossings (sign change in signal)
zero_crossings = np.where(np.diff(np.sign(raw)))[0]

# Count zero crossings
num_zero_crossings = len(zero_crossings)

# Estimate fundamental frequency (divide by 2 because a full cycle has 2 zero crossings)
estimated_frequency = (num_zero_crossings / duration) / 2

# Print results
print(f"Number of Zero Crossings: {num_zero_crossings}")
print(f"Duration: {duration:.4f} s")
print(f"Estimated Frequency: {estimated_frequency:.2f} Hz")

# Plot waveform and zero crossings
plt.figure(figsize=(12, 4))
plt.plot(raw, label="Waveform", color="blue", alpha=0.7)
plt.scatter(zero_crossings, raw[zero_crossings], color="red", label="Zero Crossings", s=10)
plt.title("Zero Crossings and Estimated Frequency")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()
