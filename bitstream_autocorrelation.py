import wave
import numpy as np
import math
from matplotlib.pyplot import figure, show

# --- Load WAV file ---
file_path = "plucks/pluck_cropped_87.31Hz_converted.wav"

with wave.open(file_path, 'rb') as wf:
    n_channels = wf.getnchannels()
    sampwidth = wf.getsampwidth()
    framerate = wf.getframerate()
    n_frames = wf.getnframes()
    raw_bytes = wf.readframes(n_frames)

print(framerate)

# Convert bytes to numpy array
dtype = np.int16 if sampwidth == 2 else np.uint8
raw_audio = np.frombuffer(raw_bytes, dtype=dtype)

# If stereo, take only one channel
if n_channels > 1:
    raw_audio = raw_audio[::n_channels]

# --- Crop to first 1000 samples ---
raw_audio = raw_audio[:1000]

# Normalize audio
audio = raw_audio / np.max(np.abs(raw_audio))
t = np.linspace(0, len(audio) / framerate, num=len(audio))

# --- Visualization and Triggering ---
fig = figure(1)

# Plot waveform
ax1 = fig.add_subplot(311)
ax1.plot(t, audio)
ax1.grid(True)
ax1.set_ylim((-1, 1))
ax1.set_title("Waveform")


# Trigger function
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

# Plot trigger
ax2 = fig.add_subplot(312)
ax2.plot(t, trig)
ax2.grid(True)
ax2.set_ylim((-0.1, 1.1))
ax2.set_title("Binary Trigger")


# XOR autocorrelation
def count_ones(l):
    return sum(1 for e in l if e)


results = []
leng = math.floor(len(trig) / 2)
for i in range(leng):
    x = [a ^ b for a, b in zip(trig[0:leng], trig[i:i+leng])]
    results.append(count_ones(x))
results.extend(results)

# Plot autocorrelation
ax3 = fig.add_subplot(313)
ax3.plot(results)
ax3.grid(True)
ax3.set_ylim((-5, max(results) + 10))
ax3.set_title("Autocorrelation (XOR of Triggers)")

# --- Estimate Frequency ---
skip = 20  # number of samples to skip
search_range = results[skip:leng]
notch_index_relative = np.argmin(search_range)
notch_index = notch_index_relative + skip

estimated_period = notch_index / framerate
estimated_frequency = 1 / estimated_period if estimated_period > 0 else 0

print(f"Estimated Frequency: {estimated_frequency:.2f} Hz")

show()
