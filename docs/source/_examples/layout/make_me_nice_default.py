import matplotlib.pyplot as plt
import mplutils as mplu

# ax = plt.subplot()
# plt.gcf().set_layout_engine(mplu.FixedAxesLayoutEngine())
fig, ax = plt.subplots(layout=mplu.FixedAxesLayoutEngine())

ax.set_xlabel("An X-Label")
ax.set_ylabel("A Y-Label")
ax.set_title("A Title")

mplu.set_axes_size_inches(8)

plt.show()
