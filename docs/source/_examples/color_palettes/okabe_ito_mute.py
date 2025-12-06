import mplutils as mplu
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.patches import Rectangle

palette = mplu.okabe_ito_muted

ax = plt.subplot()
ax.axis("off")
ax.set_aspect("equal")

for i, color in enumerate(palette):
    ax.add_patch(Rectangle((i, 0), 1, 1, facecolor=color))
    ax.text(i + 0.5, 0.5, f"{to_hex(color)}", ha="center", va="center", c="k")

ax.set_xlim(0, len(palette))

mplu.set_axes_size_inches(len(palette), len(palette))
mplu.make_me_nice(fix_figwidth=False)
