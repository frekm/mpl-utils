import matplotlib.pyplot as plt
import numpy as np
import mplutils as mplu

plt.rcParams["image.aspect"] = "auto"

fig, axs = plt.subplots(1, 2, layout=mplu.FixedLayoutEngine())

image = np.random.rand(10, 10)

im0 = axs[0].imshow(image)
im1 = axs[1].imshow(image)

mplu.add_colorbar(im0, ax=axs[0])
mplu.add_colorbar(im1, ax=axs[1], thickness=8.0, pad=4.0, location="top")

for ax in axs:
    mplu.set_axes_size(2.5, ax=ax)

# the colorbar placement shifts the axes position, we need to realign it
mplu.align_axes_vertically(*axs, alignment="bottom")
