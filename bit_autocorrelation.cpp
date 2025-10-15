#include "bit_autocorrelation.h"

constexpr int BUFFER_SIZE = 2048;

std::array<int, BUFFER_SIZE> autocorrelate(const std::array<int, BUFFER_SIZE>& data){
    std::array<int, BUFFER_SIZE> result = {};
    const auto size = data.size();
    result[0] = 0;
    for (std::size_t skip = 1; skip < size/2; ++skip) {
        int zero_count = 0;
        for (std::size_t i = 0; i < size/2; ++i) { 
            zero_count += data[i] ^ data[i + skip];
        }
        result[skip] = zero_count;
    }

    return result;
}

std::array<int, BUFFER_SIZE> zero_cross(const std::array<float, BUFFER_SIZE>& data){
    std::array<int, BUFFER_SIZE> result = {};
    for (std::size_t i = 0; i < data.size(); ++i) {
        result[i] = data[i] > 0.0f ? 1 : 0;
        
    }
    return result;
}

int main() {
    std::array<float, BUFFER_SIZE> signal = {};
    // Sample_rate/frequency must be less than BUFFER_SIZE/2
    int sample_rate = 80000.0f;
    float frequency = 250;
    float p  = float(sample_rate) / frequency;
    for (std::size_t i = 0; i < signal.size(); ++i) {
        signal[i] = 0.3 * sin(2 * M_PI * i / p) + 0.4 * sin(4 * M_1_PI * i / p) + 0.3 * sin(6 * M_PI * i / p);
    }

    auto binary_signal = zero_cross(signal);
    auto autocorr_result = autocorrelate(binary_signal);
    int min_count = BUFFER_SIZE;

    for (std::size_t i = 50; i < BUFFER_SIZE/2; ++i) {
        if (autocorr_result[i] < min_count) {
            min_count = autocorr_result[i];
        }
        std::cout << "Lag " << i << ": " << autocorr_result[i] << "\n";
    }

    constexpr auto mid_pos = BUFFER_SIZE / 2;
    for (int i = 50; i < mid_pos; i++) {
        if (autocorr_result[i] <= min_count + 2) {
            std::cout << "Period at skip: " << i << "\n";
            std::cout << "Estimated frequency: " << sample_rate / i << " Hz\n";
            break;
        }
    }

    return 0;
}