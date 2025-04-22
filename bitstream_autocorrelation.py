import wave
import numpy as np
import math
from matplotlib.pyplot import figure, show
import time

# ==============================================================================
#  Copyright (c) 2014-2018 Joel de Guzman. All rights reserved.
#
#  Distributed under the Boost Software License, Version 1.0. (See accompanying
#  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
# ==============================================================================

"""
To enhance the accuracy of the frequency estimator, we can use a Genetic Algorithm (GA) to optimize the following parameters (genes):

Genes:
- Lower threshold (-0.1 now)
- Upper threshold (0.1 now)
- Number of samples to skip: how far to skip when searching for the first autocorrelation notch (20 now)
- Number of samples to consider: how much of the waveform to use for analysis (e.g., 800 vs 1000 samples; 1000 now)

These genes can be adjusted automatically by the GA to minimize estimation error.

Fitness function:
- 1 / (1.0 + total squared error across multiple test samples)
- A maximum allowed time could also be considered
- The goal is to find gene settings that result in the smallest difference between estimated and true frequency

To evaluate the fitness:
- Run the frequency estimator with a given set of gene values
- Compare estimated frequency to the true known value (e.g., extracted from the filename)
- Repeat this over multiple .wav files to avoid overfitting to a single case

For better results:
- Consider adding artificial noise to some inputs
- Use early portions of the waveform (attack phase) where pitch is most stable
"""

start_time = time.time()  # record start time

# --- Load WAV file ---
file_path = "plucks/pluck_cropped_87.31Hz_converted.wav"

# Extract true frequency from filename, e.g. "pluck_cropped_98Hz_converted.wav"
try:
    freq_part = file_path.split("_")[2]
    true_freq = float(freq_part.replace("Hz", ""))
except Exception as e:
    print(e)
    true_freq = None

with wave.open(file_path, 'rb') as wf:
    n_channels = wf.getnchannels()
    sampwidth = wf.getsampwidth()
    framerate = wf.getframerate()
    n_frames = wf.getnframes()
    raw_bytes = wf.readframes(n_frames)

# print(framerate)  # debugging

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

print(f"True frequency: {true_freq:.2f} Hz")

print(f"Time to estimate: {time.time() - start_time} seconds")

show()
