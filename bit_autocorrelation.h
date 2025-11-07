#ifndef BIT_AUTOCORRELATION_H
#define BIT_AUTOCORRELATION_H

#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <type_traits>
#include <vector>
#include <chrono>

// Function to convert waveform to binary (1 for positive, 0 for negative)
std::vector<int16_t> zero_cross(const std::vector<int16_t>& waveform);

// Function to compute the bitwise autocorrelation
std::vector<uint32_t> autocorrelate(const std::vector<int16_t>& binary_wave);

#endif