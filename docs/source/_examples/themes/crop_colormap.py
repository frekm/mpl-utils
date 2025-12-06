import matplotlib.pyplot as plt
import numpy as np
import mplutils as mplu

data = np.linspace(0, 1, 90).reshape(30, 3)  # some data to plot

plt.rcParams["image.aspect"] = "auto"

viridis = plt.cm.get_cmap("viridis")
viridis_cropped = mplu.crop_colormap(viridis, 0.3, 0.7)

_, axs = plt.subplots(1, 2)
for ax in axs:
    mplu.set_axes_size_inches(2.5, ax=ax)


axs[0].set_title("default colormap (viridis)")
im0 = axs[0].imshow(data, cmap=viridis)
mplu.add_colorbar(im0, axs[0])


axs[1].set_title("cropped colormap (viridis)")
im1 = axs[1].imshow(data, cmap=viridis_cropped)
mplu.add_colorbar(im1, axs[1])

mplu.make_me_nice()
