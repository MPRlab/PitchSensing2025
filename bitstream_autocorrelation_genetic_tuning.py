import wave
import numpy as np
import os
import pygad  # For the genetic algorithm
import math
from matplotlib import pyplot as plt

# Folder containing the input .wav files
folder_path = "plucks"


# ----------------- Core Estimator -----------------
def estimate_freq_via_xor_trigger(file_path, low_thresh=-0.1, high_thresh=0.1, num_samples=1000, samples_to_skip=20):
    with wave.open(file_path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    dtype = np.int16 if sampwidth == 2 else np.uint8
    raw_audio = np.frombuffer(raw_bytes, dtype=dtype)

    if n_channels > 1:
        raw_audio = raw_audio[::n_channels]

    raw_audio = raw_audio[:num_samples]
    audio = raw_audio / np.max(np.abs(raw_audio))

    class zero_cross:
        def __init__(self):
            self.y = 0

        def __call__(self, s):
            if s < low_thresh:
                self.y = 0
            elif s > high_thresh:
                self.y = 1
            return self.y

    zc = zero_cross()
    trig = [zc(s) for s in audio]

    def count_ones(l):
        return sum(1 for e in l if e)

    results_autocorr = []
    leng = math.floor(len(trig) / 2)
    for i in range(leng):
        x = [a ^ b for a, b in zip(trig[0:leng], trig[i:i + leng])]
        results_autocorr.append(count_ones(x))
    results_autocorr.extend(results_autocorr)

    skip = samples_to_skip
    search_range = results_autocorr[skip:leng]
    if not search_range:
        return 0.0
    notch_index_relative = np.argmin(search_range)
    notch_index = notch_index_relative + skip

    estimated_period = notch_index / framerate
    estimated_frequency = 1 / estimated_period if estimated_period > 0 else 0

    return estimated_frequency


# ----------------- Fitness Function -----------------
# Pre-load the dataset once so GA runs faster
test_files = []
true_freqs = []
for filename in os.listdir(folder_path):
    # Do not consider artificially created samples
    if "converted" in filename and filename.endswith(".wav") and "artificial" not in filename:
        input_path = os.path.join(folder_path, filename)
        try:
            freq_part = filename.split("_")[2]  # get true frequency from the file's name
            true_freq = float(freq_part.replace("Hz", ""))
            true_freqs.append(true_freq)
            test_files.append((input_path, true_freq))
        except Exception as e:
            print("Error encountered: {e}")
            continue


def fitness_func(ga_instance, solution, solution_idx):
    low_thresh, high_thresh, samples_to_skip, num_samples = solution

    total_error = 0.0

    for file_path, true_freq in test_files:
        est_freq = estimate_freq_via_xor_trigger(
            file_path,
            low_thresh=low_thresh,
            high_thresh=high_thresh,
            samples_to_skip=int(samples_to_skip),
            num_samples=int(num_samples)
        )
        total_error += (est_freq - true_freq) ** 2  # Use square error to punish outliers

    fitness = 1.0 / (1.0 + total_error)  # Lower error = higher fitness
    return fitness


# ----------------- PyGAD Setup -----------------

gene_space = [
    {'low': -0.2, 'high': -0.0},    # low_thresh
    {'low': 0.1,  'high': 0.4},    # high_thresh
    {'low': 0,    'high': 30},    # samples_to_skip
    {'low': 400,  'high': 2000}    # num_samples
]

ga_instance = pygad.GA(
    num_generations=100,
    num_parents_mating=5,
    fitness_func=fitness_func,
    sol_per_pop=50,
    num_genes=4,
    gene_space=gene_space,
    parent_selection_type="rank",
    crossover_type="single_point",
    mutation_type="random",
    mutation_percent_genes=40
)

# ----------------- Run GA -----------------
ga_instance.run()

# ----------------- Results -----------------
solution, solution_fitness, solution_idx = ga_instance.best_solution()
print(f"Best Solution: {solution}")
print(f"Fitness of Best Solution: {solution_fitness}")

best_low_thresh, best_high_thresh, best_samples_to_skip, best_num_samples = solution
print(f"Best Params:")
print(f"  Low Threshold: {best_low_thresh}")
print(f"  High Threshold: {best_high_thresh}")
print(f"  Samples to Skip: {int(best_samples_to_skip)}")
print(f"  Number of Samples: {int(best_num_samples)}")

print(f"Default Params:")
print(f"  Low Threshold: {-0.1}")
print(f"  High Threshold: {0.1}")
print(f"  Samples to Skip: {20}")
print(f"  Number of Samples: {1000}")

# --- Collect results ---
untuned_estimates = []
tuned_estimates = []

for file_path, true_freq in test_files:
    # Untuned (default parameters)
    untuned_freq = estimate_freq_via_xor_trigger(
        file_path
    )
    untuned_estimates.append(untuned_freq)

    # Tuned
    low_thresh_tuned, high_thresh_tuned, samples_to_skip_tuned, num_samples_tuned = solution
    tuned_freq = estimate_freq_via_xor_trigger(
        file_path,
        low_thresh=low_thresh_tuned,
        high_thresh=high_thresh_tuned,
        num_samples=int(num_samples_tuned),
        samples_to_skip=int(samples_to_skip_tuned)
    )
    tuned_estimates.append(tuned_freq)

# --- Plot results ---
plt.figure(figsize=(12, 6))
plt.plot(true_freqs, label='True Frequency', marker='o')
plt.plot(untuned_estimates, label='Untuned Estimate', marker='x')
plt.plot(tuned_estimates, label='Tuned Estimate', marker='s')
plt.xlabel('Sample Index')
plt.ylabel('Frequency (Hz)')
plt.title('True vs Untuned vs Tuned Frequency Estimates')
plt.legend()
plt.grid()
plt.show()
