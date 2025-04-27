import librosa
import soundfile as sf
import os

# Define paths
input_path = os.path.expanduser("plucks/pluck_cropped_212Hz_converted.wav")
output_path = os.path.expanduser("plucks/pluck_cropped_212Hz_converted.wav")

# Load original audio
data, sr = librosa.load(input_path, sr=None)

# Resample to 44100 Hz
resampled = librosa.resample(data, orig_sr=sr, target_sr=44100)

# Save the converted file
sf.write(output_path, resampled, 44100)
