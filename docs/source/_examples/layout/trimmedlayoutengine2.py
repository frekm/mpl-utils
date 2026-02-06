import matplotlib.pyplot as plt
import mplutils as mplu

fig, ax = plt.subplots(layout=mplu.TrimmedLayoutEngine())
fig.set_facecolor("#afafaf")

ax.set_box_aspect(1.0)  # empty space left/right of ax is trimmed
