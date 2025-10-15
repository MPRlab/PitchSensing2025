all: bit_autocorrelation.o audio_pitch_detection.o
	g++ bit_autocorrelation.o audio_pitch_detection.o -o audio_detect

bit_autocorrelation.o: bit_autocorrelation.cpp bit_autocorrelation.h
	g++ bit_autocorrelation.cpp -c -o bit_autocorrelation.o

audio_pitch_detection.o: audio_pitch_detection.cpp audio_pitch_detection.h bit_autocorrelation.h bit_autocorrelation.cpp
	g++ audio_pitch_detection.cpp -c -o audio_pitch_detection.o