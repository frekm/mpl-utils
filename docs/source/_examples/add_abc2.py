import matplotlib.pyplot as plt
import numpy as np
import mplutils as mplu

fig, axs = plt.subplots(2, 3, layout="compressed")

fig.suptitle("add_abc(): Offsets according to margins")

xoffsets = np.empty_like(axs, dtype=float)
yoffsets = np.empty_like(axs, dtype=float)
lim = 1.0

for (i, j), ax in np.ndenumerate(axs):
    ax.set_ylim(0, lim)
    lim *= 10
    margins = mplu.get_axes_margins(ax)
    xoffsets[i, j] = -margins[3] - 5.0
    yoffsets[i, j] = margins[0]

mplu.add_abc(xoffset_pts=xoffsets, yoffset_pts=yoffsets, ha="right", va="top")
