import mplutils as mplu
import numpy as np
import matplotlib.pyplot as plt

ax1 = plt.subplot(121, polar=True)
ax2 = plt.subplot(122, polar=True)

theta = np.linspace(0, 2 * np.pi, 1000)
y = 0.5 * (5 * np.cos(theta) ** 2 - 1)

for ax in ax1, ax2:
    ax.plot(theta, y)
    ax.set_ylim(bottom=0)

mplu.square_polar_axes(ax2)

mplu.make_me_nice()
