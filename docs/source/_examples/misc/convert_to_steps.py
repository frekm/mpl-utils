import matplotlib.pyplot as plt
import numpy as np
import mplutils as mplu

x = np.linspace(1.0, 10.0, 9)
y = 2.0 * x

fig, axs = plt.subplots(1, 3)

axs[0].plot(x, y, "-")
axs[1].plot(*mplu.convert_to_steps(x, y), "-")
axs[2].plot(*mplu.convert_to_steps(x, y, start_at="auto"), "-")

for ax in axs:
    mplu.set_axes_size_inches(2.5, 3.0 / 4.0, ax=ax)

mplu.make_me_nice()
