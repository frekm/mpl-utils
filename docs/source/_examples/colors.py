import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.patheffects as patheffects
import mplutils as mplu

fig, ax = plt.subplots(layout=mplu.FixedLayoutEngine())

colors = mplu.Colors()

y = 3
for i, (name, color) in enumerate(vars(colors).items()):
    x = i % 4
    ax.add_patch(mpatches.Rectangle((x, y), 1.0, 1.0, facecolor=color))
    t0 = ax.text(x + 0.5, y + 0.55, name, ha="center", va="bottom", c="w")
    t1 = ax.text(
        x + 0.5, y + 0.45, f"{mcolors.to_hex(color)}", ha="center", va="top", c="w"
    )
    if x == 3:
        y -= 1
    for text in (t0, t1):
        text.set_path_effects(
            [
                patheffects.withStroke(linewidth=1.5, foreground="k"),
                patheffects.Normal(),
            ]
        )

ax.set_xlim(0, 4)
ax.set_ylim(0, 4)
ax.axis("off")
mplu.set_axes_size(4)
