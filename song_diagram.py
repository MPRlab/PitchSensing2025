import wave, struct, random, math
import matplotlib.pyplot as plt
import numpy as np

def mean(a):
    return sum(a)/len(a)

def split_arr(a, ln):
    #Ищем количество маленьких массивов
    split_a = [[] for i in range(math.ceil(len(a) / ln))]
    c = 0
    for i in a:
        split_a[c//ln].append(i)
        c += 1
    return split_a

def split_mean(a, ln):
    split_a = split_arr(a, ln)
    split_mean_arr = []
    for i in split_a:
        avg = mean(i)
        for j in range(ln):
            if len(split_mean_arr) < len(a):
                split_mean_arr.append(avg)
    return split_mean_arr

def split_max(a, ln):
    split_a = split_arr(a, ln)
    split_max_arr = []
    for i in split_a:
        maxi = max(i)
        for j in range(ln):
            if len(split_max_arr) < len(a):
                split_max_arr.append(maxi)
    return split_max_arr

#Название файла с песней
song_file = "sound.wav"

song = wave.open(song_file, "r")
raw0 = song.readframes(-1)

#Обрезка фрагмента
#raw0 = raw0[0:int(rate*symbols_in_sample*8):]

raw = np.frombuffer(raw0, dtype=np.int32)
sample_rate = song.getframerate()
raw = [abs(i)/100 for i in raw]

#Частота поиска максимума
rate = 5000

#Максимумы громкости
max_arr = split_max(raw, rate)

#Средний максимум
max_avg = mean(max_arr)

plt.title("Waveform")
plt.plot(raw, color="blue")
plt.plot(max_arr, color="red")
plt.plot([i if (i > max_avg) and (i in max_arr) else 0 for i in raw], color="green")
plt.plot([max_avg for i in raw], color="#ff891e")
plt.ylabel("Amplitude")
plt.xlabel("Time")
plt.show()
