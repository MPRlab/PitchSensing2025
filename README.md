### TL;DR: we have found that bitstream [autocorrelation](https://en.m.wikipedia.org/wiki/Autocorrelation) is the most effective explored method for real-time audio frequency estimation in terms of runtime (< 0.7s) and accuracy (± 2 Hz).

### For list of things to do, check TODO.md

# Frequency Estimation from Audio Files

This project analyzes a folder of `.wav` audio files (specifically plucked sounds) and estimates their fundamental frequencies using multiple methods:
- Basic zero-crossing counting
- Zero-crossing counting after low-pass filtering
- XOR-based bitstream autocorrelation

It saves the analysis results into an Excel spreadsheet for easy comparison with the known ("true") frequencies.

The project also includes a genetic algorithm setup used to tune bitstream autocorrelation parameters (bitstream_autocorrelation_genetic_tuning.py)

---

## How It Works

1. **Zero Crossing Count**  
   Detects how many times the audio waveform crosses zero, then estimates the frequency based on the number of crossings.

2. **Zero Crossing + Low-Pass Filter (500Hz)**  
   Applies a simple low-pass filter to clean up noise before counting zero crossings, giving more reliable results on noisy data.

3. **XOR Autocorrelation**  
   Binarizes the audio signal using a Schmitt trigger with two parameters (low and high thresholds) and computes an XOR-based autocorrelation. Finds the first minimum in the result to estimate the period and thus the frequency.
   For more information, see [Joel de Guzman's research](https://www.cycfi.com/2018/03/fast-and-efficient-pitch-detection-bitstream-autocorrelation/)

---

## How to Use

1. Place all your `.wav` files in a folder called `plucks/`.  
   Filenames should include the true frequency for comparison, e.g., `pluck_cropped_98Hz_converted.wav`.

2. Run the main script.  
   It will:
   - Process each file
   - Apply the different frequency estimation methods
   - Collect all results

3. After completion, a results table will be saved as:  
   ```
   tables/zero_crossings_auto_generated_table.xlsx
   ```

---

## Requirements

- Python 3.x
- Libraries:
  - `numpy`
  - `pandas`
  - `pydub`
  - `wave`
  - `os`
  - `math`

Install the required Python libraries using:
```bash
pip install numpy pandas pydub
```

---

## Project Structure

| File/Folders        | Description                                |
|---------------------|--------------------------------------------|
| `plucks/`           | Folder containing input `.wav` files       |
| `tables/`           | Output folder where results Excel file will be saved |
| `frequency_estimator.py`    | Main processing and analysis code          |
| `bitstream_autocorrelation_genetic_tuning.py` | Genetic algorithm used to tune the autocorrelation algorithm |

---

## Notes

- Only files containing the substring `"converted"` and ending with `.wav` are processed.
- Temporary filtered audio is saved as `temp_filtered.wav` during processing.
- The XOR autocorrelation method is adapted from public domain code by Joel de Guzman.

---

## Credits

- XOR Autocorrelation method:  
  © 2014-2018 Joel de Guzman — Boost Software License 1.0.
