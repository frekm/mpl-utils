import matplotlib.pyplot as plt
import mplutils as mplu
import numpy as np

fig, axs = plt.subplots(2, 3)

axs[0, 1].set_ylim(0, 1000)
axs[1, 2].set_ylim(0, 1.1)
axs[0, 0].set_ylabel("A Label")

fig.suptitle("add_abc(): Offsets corresponding to margins")

offsets = np.empty((2, *axs.shape))
for (i, j), ax in np.ndenumerate(axs):
    margins = mplu.get_axes_margins_inches(ax)
    offsets[0, i, j] = margins.left * mplu.PTS_PER_INCH + 2.0
    offsets[1, i, j] = margins.top * mplu.PTS_PER_INCH + 2.0

mplu.add_abc(xoffset_pts=-offsets[0], yoffset_pts=offsets[1], ha="right")

mplu.make_me_nice(margin_pad_pts=(25, 3, 3, 3))
