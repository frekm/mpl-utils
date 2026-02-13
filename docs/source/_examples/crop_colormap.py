import matplotlib.pyplot as plt
import mplutils as mplu

viridis = plt.cm.get_cmap("viridis")
viridis_cropped = mplu.crop_colormap(viridis, 0.3, 0.7)
cmaps = viridis, viridis_cropped

fig, axs = plt.subplots(2, 1, layout=mplu.FixedLayoutEngine())

titles = "default colormap (viridis)", "cropped colormap (viridis)"
for ax, title, cmap in zip(axs, titles, cmaps):
    fig.colorbar(plt.cm.ScalarMappable(cmap=cmap), cax=ax, orientation="horizontal")
    ax.set_title(title)
    mplu.set_axes_size(7, 1.0, ax=ax)
