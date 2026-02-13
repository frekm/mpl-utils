import matplotlib.pyplot as plt
import mplutils as mplu

fig, axs = plt.subplots(3, 2, layout=mplu.FixedLayoutEngine())
fig.set_facecolor("grey")

for ax in axs.flat:
    mplu.set_axes_size(2.5, ax=ax)
