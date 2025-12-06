import matplotlib.pyplot as plt
import mplutils as mplu

fig, axs = plt.subplots(2, 3)

fig.suptitle("add_abc(): Different offsets")

mplu.add_abc(xoffset_pts=(5, 15, 20), yoffset_pts=((-12, -15, -18), (-21, -24, -27)))

mplu.make_me_nice(margin_pad_pts=(25, 3, 3, 3))
