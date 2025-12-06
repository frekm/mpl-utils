import mplutils as mplu
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# some data to plot
fr = 0.5
to = 1.5
size = 1000
data = np.linspace(-fr, to, size).reshape(size, 1)
hist = np.arange(size + 1), np.arange(2), data.T

plt.rcParams["image.cmap"] = "RdBu"
plt.rcParams["image.aspect"] = "auto"
_, axs = plt.subplots(1, 3)

for ax in axs:
    mplu.set_axes_size_inches(2.5, ax=ax)
    zero_crossing = fr * size / (fr + to)
    ax.axvline(zero_crossing)
    ax.text(zero_crossing + 10, 0.95, "zero crossing", va="top")

norm1 = mcolors.TwoSlopeNorm(vmin=-fr, vcenter=0, vmax=to)
norm2 = mcolors.TwoSlopeNorm(vmin=-max(fr, to), vcenter=0, vmax=max(fr, to))

titles = (
    "Misaligned zero",
    "Different dynamic range ",
    "Equal dynamic range",
)

for i, norm in enumerate((None, norm1, norm2)):
    im = axs[i].pcolormesh(*hist, norm=norm, rasterized=True)

    axs[i].set_title(titles[i], pad=40)

    cb = mplu.add_colorbar(im, axs[i], location="top")
    cb.ax.set_xlim(-fr, to)
    cb.ax.axvline(0)

mplu.make_me_nice()
