import matplotlib.pyplot as plt
import numpy as np
import mplutils as mplu

x = np.linspace(1.0, 10.0, 9)
y = 2.0 * x

_, axs = plt.subplots(1, 3, layout=mplu.FixedLayoutEngine())

axs[0].plot(x, y, "-")
axs[1].plot(*mplu.convert_to_steps(x, y), "-")
axs[2].plot(*mplu.convert_to_steps(x, y, start_at="auto"), "-")

for ax in axs:
    mplu.set_axes_size(2.5, aspect=3.0 / 4.0, ax=ax)
