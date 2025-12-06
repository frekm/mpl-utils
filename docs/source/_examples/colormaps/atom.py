import mplutils as mplu
import matplotlib.pyplot as plt
import numpy as np

gradient = np.linspace(0.0, 1.0, 256)
gradient = np.vstack((gradient, gradient))

_, axs = plt.subplots(nrows=2)
for ax, cmap in zip(axs, ("atom", "atom_from_white")):
    ax.imshow(gradient, aspect="auto", cmap=cmap)
    ax.text(-0.01, 0.5, cmap, va="center", ha="right", transform=ax.transAxes)
    ax.set_axis_off()
    mplu.set_axes_size_inches(4.0, 1.0 / 8.0, ax)

mplu.make_me_nice()
