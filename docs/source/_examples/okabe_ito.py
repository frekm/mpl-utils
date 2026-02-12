import mplutils as mplu
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.patches import Rectangle

palette = mplu.OkabeItoPalette()

ax = plt.subplot()
plt.gcf().set_layout_engine(mplu.FixedLayoutEngine())
ax.axis("off")

for i, color in enumerate(palette):
    ax.add_patch(Rectangle((i, 0), 1, 1, facecolor=color))
    ax.text(i + 0.5, 0.5, f"{to_hex(color)}", ha="center", va="center", c="w")

ax.set_xlim(0, len(palette))
mplu.set_axes_size(len(palette), 1.0)

plt.show()
