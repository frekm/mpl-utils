import matplotlib.pyplot as plt
import mplutils as mplu


def print_dimensions(fig, ax, y, when):
    kwargs = dict(va="top", ha="right")
    axsize = ", ".join([f"{s:.1f}" for s in mplu.get_axes_size_inches(ax)])
    figsize = ", ".join([f"{s:.1f}" for s in fig.get_size_inches()])
    margins = ", ".join([f"{s:.1f}" for s in mplu.get_margins_pts()])
    ax.text(0.95, y, f"Axes size {when}: ({axsize}) inch", **kwargs)
    ax.text(0.95, y - 3 * 0.05, f"Figure size {when} : ({figsize}) inch", **kwargs)
    ax.text(0.95, y - 3 * 0.1, f"Margins size {when}: ({margins}) pts", **kwargs)


ax = plt.subplot()
fig = plt.gcf()

ax.set_xlabel("An X-Label")
ax.set_ylabel("A Y-Label")
ax.set_title("A Title")

print_dimensions(fig, ax, 0.95, "before")

mplu.make_me_nice(fix_figwidth=True)

print_dimensions(fig, ax, 0.9, "after")
