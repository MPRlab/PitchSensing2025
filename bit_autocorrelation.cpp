#include "bit_autocorrelation.h"

constexpr int BUFFER_SIZE = 2048;

std::vector<uint32_t> autocorrelate(const std::vector<int16_t>& data){
    std::vector<uint32_t> result = {};
    const auto size = data.size();
    std::cout << "Data size: " << size << "\n";
    result.push_back(0);
    for (std::size_t skip = 1; skip < size/2; ++skip) {
        int zero_count = 0;
        for (std::size_t i = 0; i < size/2; ++i) { 
            zero_count += data.at(i) ^ data.at(i + skip);
        }
        result.push_back(zero_count);
    }
    return result;
}

std::vector<int16_t> zero_cross(const std::vector<int16_t>& data){
    std::vector<int16_t> result = {};
    for (std::size_t i = 0; i < data.size(); ++i) {
        result.push_back(data.at(i) > 0.0f ? 1 : 0);
    }
    return result;
}