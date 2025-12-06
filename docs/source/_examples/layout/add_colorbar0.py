import matplotlib.pyplot as plt
import numpy as np
import mplutils as mplu

image = np.linspace(0, 1, 100).reshape(10, 10)

im = plt.imshow(image)

cb = mplu.add_colorbar(im)
cb.set_label("My Label")

mplu.make_me_nice()
