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

    // Basic validation (e.g., check for "RIFF", "WAVE", "fmt ", "data")
    // ...

    // Move to the data chunk
    // (In a real implementation, you'd parse chunks to find the 'data' chunk)
    file.seekg(sizeof(WavHeader)); 

    std::vector<int16_t> samples;
    int16_t sample;
    while (file.read(reinterpret_cast<char*>(&sample), sizeof(int16_t))) {
        samples.push_back(sample);
    }
    std::cout << "Total samples read: " << samples.size() << "\n";

    file.close();

    return samples;
}

int main() {
    std::vector<int16_t> waveform = getWaveformData("plucks_pluck_cropped_116.2Hz_converted.wav");
    if (waveform.empty()) {
        std::cerr << "Failed to load waveform data." << std::endl;
        return -1;
    }
    std::vector<int16_t> binary_wave = zero_cross(waveform);
    std::vector<int16_t> autocorr_result = autocorrelate(binary_wave);
    std::cout << "Autocorrelation result size: " << autocorr_result.size() << "\n";

    int min_count = waveform.size();
    for (std::size_t i = 50; i < waveform.size()/2; ++i) {
        if (autocorr_result.at(i) < min_count) {
            min_count = autocorr_result.at(i);
        }
    }
    auto mid_pos = waveform.size() / 2;
    for (int i = 50; i < mid_pos; i++) {
        if (autocorr_result[i] <= min_count + 2) {
            std::cout << "Period at skip: " << i << "\n";
            std::cout << "Estimated frequency: " << 44100 / i << " Hz\n";
            break;
        }
    }
    return 0;
}