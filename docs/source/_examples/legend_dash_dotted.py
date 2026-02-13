import matplotlib.pyplot as plt
import mplutils as mplu

_, (ax0, ax1) = plt.subplots(1, 2, layout=mplu.FixedLayoutEngine())

ax0.plot([0, 1], ls="dashdot", label="incorrect width")
ax0.plot([1, 2], ls="-", label="reference width")
ax1.plot([0, 1], ls=mplu.dash_dotted(), label="correct width")
ax1.plot([1, 2], ls="-", label="reference width")

for ax in (ax0, ax1):
    mplu.set_axes_size(2.5, ax=ax)
    ax.legend()
