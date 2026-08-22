// (Simplified) Example structure for WAV header (actual structure is more complex)
#include "audio_pitch_detection.h"

struct WavHeader {
    char riff_id[4];
    uint32_t file_size;
    char wave_id[4];
    char fmt_id[4];
    uint32_t fmt_size;
    uint16_t audio_format;
    uint16_t num_channels;
    uint32_t sample_rate;
    uint32_t byte_rate;
    uint16_t block_align;
    uint16_t bits_per_sample;
    char data_id[4];
    uint32_t data_size;
};

// Function to get waveform data (simplified for illustration)
std::vector<int16_t> getWaveformData(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return {};
    }

    WavHeader header;
    file.read(reinterpret_cast<char*>(&header), sizeof(WavHeader));
    std::cout << "Sample Rate: " << header.sample_rate << "\n";
    std::cout << "Bits per Sample: " << header.bits_per_sample << std::endl;

    // Basic validation (e.g., check for "RIFF", "WAVE", "fmt ", "data")
    // ...

    // Move to the data chunk
    // (In a real implementation, you'd parse chunks to find the 'data' chunk)
    file.seekg(sizeof(WavHeader)); 

    std::vector<int16_t> samples;
    int16_t sample;
    int sample_count = 0;
    while (file.read(reinterpret_cast<char*>(&sample), sizeof(int16_t)) && sample_count < 8192) {
        samples.push_back(sample);
        sample_count++;
    }
    std::cout << "Total samples read: " << samples.size() << "\n";

    file.close();

    return samples;
}

int main() {
    std::vector<int16_t> waveform = getWaveformData("./audio/artificialplucknoisy_cropped_80Hz_converted.wav");
    if (waveform.empty()) {
        std::cerr << "Failed to load waveform data." << std::endl;
        return -1;
    }
    std::vector<int16_t> binary_wave = zero_cross(waveform);
    auto start = std::chrono::high_resolution_clock::now();
    std::vector<uint32_t> autocorr_result = autocorrelate(binary_wave);
    int min_count = waveform.size();
    for (std::size_t i = 50; i < waveform.size() / 2; ++i) {
        if (autocorr_result.at(i) < min_count) {
            min_count = autocorr_result.at(i);
        }
    }
    auto mid_pos = waveform.size() / 2;
    int mins_count = 0;
    int previous_min = 0;
    float total_freqs = 0.0;
    for (int i = 50; i < mid_pos; i++) {
        if (autocorr_result[i] <= min_count + 2) {
            mins_count++;
            total_freqs += 44100.0 / (float) (i - previous_min);
            previous_min = i;
            i += 10;
        }
    }
    std::cout << autocorr_result[476] << std::endl;
    std::cout << autocorr_result[942] << std::endl;
    std::cout << "Estimated frequency: " << total_freqs / ( float)mins_count << std::endl;
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::cout << "Execution time: " << duration.count() << " milliseconds" << std::endl;
    return 0;
}