import matplotlib.pyplot as plt
import mplutils as mplu

fig, axs = plt.subplots(2, 3)

fig.suptitle("add_abc(): Default")

mplu.add_abc()

mplu.make_me_nice(margin_pad_pts=(25, 3, 3, 3))
