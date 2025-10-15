all: bit_autocorrelation.o
	g++ bit_autocorrelation.o -o bit_autocorrelation
bit_autocorrelation.o: bit_autocorrelation.cpp bit_autocorrelation.h
	g++ bit_autocorrelation.cpp -c -o bit_autocorrelation.o