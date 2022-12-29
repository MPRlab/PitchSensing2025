import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt

#Название файла с песней
song_file = "C:\\Users\\79140\\Desktop\\audiobred.wav"

song = wave.open(song_file, "r")
raw0 = song.readframes(-1)
rate = 44100
symbols_in_sample = 4

#Обрезка фрагмента
#raw0 = raw0[0:int(rate*symbols_in_sample*1):]

raw = np.frombuffer(raw0, dtype=np.int32)
sample_rate = song.getframerate()
raw = [i for i in raw]

#Упрощение звука
simp_rate = 44100
raw1 = []

for i in range(len(raw) % simp_rate):
    raw.append(0)

for i in range(0, len(raw)):
    ind = (i // simp_rate) * simp_rate
    raw1.append(max(raw[ind:ind+1:]) if raw[i] == max(raw[ind:ind+1:]) else 0)

t = np.linspace(0, len(raw) / sample_rate, num=len(raw))
plt.title("Waveform")
plt.plot(t, raw1, color="blue")
plt.ylabel("Amplitude")
plt.xlabel("Time (s)")
plt.show()
