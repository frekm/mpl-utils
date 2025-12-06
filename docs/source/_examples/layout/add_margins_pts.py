import matplotlib.pyplot as plt
import mplutils as mplu

# create axes and add some labels
ax = plt.subplot()
ax.set_xlabel("An X-Label")
ax.set_ylabel("A Y-Label")
ax.set_title("A Title")

# get extra margins and remove them
extra_margins = mplu.get_margins_pts()
padding = 5.0  # pts
mplu.add_margins_pts(-extra_margins + padding)
