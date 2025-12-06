import matplotlib.pyplot as plt
import aplepy as ap

plt.rcParams["figure.facecolor"] = "grey"

# create axes and add some labels
ax = plt.subplot()
ax.set_xlabel("An X-Label")
ax.set_ylabel("A Y-Label")
ax.set_title("A Title")

im = ax.imshow([range(100)], aspect="auto")
cbar = ap.add_colorbar(im, ax)
cbar.set_label("A Z-Label")

# get extra margins and remove them
extra_margins = ap.get_margins_pts()
padding = 5.0  # pts
ap.add_margins_pts(-extra_margins + padding)
