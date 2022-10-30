import numpy as np
import matplotlib.pyplot as plt


x = np.arange(100)
Nr = 4
Nt = 4
y = np.empty((Nr, Nt, 100))
for i in range(Nr):
    for j in range(Nt):
        y[i, j] = np.full(100, i)
        y[i, j, j*25:] = 0

str_Nr = input("Nr(0~%s) = " % (Nr-1))
str_Nt = input("Nt(0~%s) = " % (Nt-1))
if str_Nr.find(" ") == -1:
    Nr_start = int(str_Nr)
    Nr_end = int(str_Nr)
    Nr_num = 1
else:
    Nr_del = str_Nr.find(" ")
    Nr_start = int(str_Nr[0:Nr_del])
    Nr_end = int(str_Nr[Nr_del+1:])
    Nr_num = Nr_end - Nr_start + 1
if str_Nt.find(" ") == -1:
    Nt_start = int(str_Nt)
    Nt_end = int(str_Nt)
    Nt_num = 1
else:
    Nt_del = str_Nt.find(" ")
    Nt_start = int(str_Nt[0:Nt_del])
    Nt_end = int(str_Nt[Nt_del+1:])
    Nt_num = Nt_end - Nt_start + 1

fig, ax = plt.subplots(Nr_num, Nt_num, squeeze=False, tight_layout=True, sharex=True, sharey=True)
print(np.shape(ax))
for i in range(Nr_num):
    for j in range(Nt_num):
        ax[i, j].plot(x, y[Nr_start+i, Nt_start+j])
plt.show()

