import numpy as np
import matplotlib.pyplot as plt


v = 1
u = 2
fig, ax = plt.subplots(v, u, squeeze=False, tight_layout=True, sharex=True, sharey=True)
print(np.shape(ax))
x = np.arange(100)
y = np.sin(x)
for i in range(v):
    for j in range(u):
        ax[i, j].plot(x, y)
plt.show()
