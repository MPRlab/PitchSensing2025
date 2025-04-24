import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import os

# Create output directory if it doesn't exist
os.makedirs("plucks", exist_ok=True)


def generate_guitar_waveform(frequency=440.0, sample_rate=44100, duration=2.0, harmonics=[1, 2, 3, 4], amplitudes=[1.0, 0.7, 0.35, 0.17], decay_rate=3.0):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = np.zeros_like(t)

    for i, harmonic in enumerate(harmonics):
        amp = amplitudes[i] if i < len(amplitudes) else 1.0 / harmonic
        waveform += amp * np.sin(2 * np.pi * frequency * harmonic * t)

    envelope = np.exp(-decay_rate * t)
    waveform *= envelope

    # Normalize to 16-bit range
    waveform /= np.max(np.abs(waveform))
    waveform_int16 = np.int16(waveform * 32767)

    # Save WAV file
    filename = f"plucks/artificialpluck_cropped_{int(frequency)}Hz.wav"
    write(filename, sample_rate, waveform_int16)

    # Plot waveform
    plt.figure(figsize=(12, 2))
    plt.plot(t[:1000], waveform[:1000])  # Show a small slice for clarity
    plt.title("Waveform")
    plt.grid(True)
    plt.show()

    return filename


# Generate for N Hz with harmonics calculated from base
generate_guitar_waveform(frequency=400.0)

