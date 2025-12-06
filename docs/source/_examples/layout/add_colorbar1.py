import matplotlib.pyplot as plt
import numpy as np
import mplutils as mplu

image = np.linspace(0.0, 1.0, 100).reshape(10, 10)

_, (ax0, ax1) = plt.subplots(1, 2)

im0 = ax0.imshow(image)
im1 = ax1.imshow(image / 10)

cb0 = mplu.add_colorbar(im0, ax0, location="top")
cb1 = mplu.add_colorbar(im1, ax1)

cb0.set_label("A label")
cb1.set_label("Another label", rotation=270, va="baseline")

mplu.make_me_nice()
