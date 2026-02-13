import matplotlib.pyplot as plt
import numpy as np
import mplutils as mplu

plt.rcParams["image.aspect"] = "auto"

fig, axs = plt.subplots(1, 2, layout=mplu.FixedLayoutEngine())

image = np.random.rand(10, 10)

axs[0].set_title("Added after resizing")
im0 = axs[0].imshow(image)
mplu.set_axes_size(2.5, ax=axs[0])
mplu.add_colorbar(im0, ax=axs[0], thickness_pts=8.0)

axs[1].set_title("Added before resizing")
im1 = axs[1].imshow(image)
mplu.add_colorbar(im1, ax=axs[1], thickness_pts=8.0)
mplu.set_axes_size(2.5, ax=axs[1])

plt.show()
