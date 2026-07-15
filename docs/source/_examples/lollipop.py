import matplotlib.pyplot as plt

import mplutils as mplu

fig, (ax0, ax1) = plt.subplots(1, 2, layout=mplu.FixedLayoutEngine())

mplu.lollipop(["A", "B", "C"], [1, 2, 3], ax=ax0)
mplu.lollipop([1, 2, 3], [3, 2, 1], ax=ax1, color="r", base=(2, 1, 0))

for ax in (ax0, ax1):
    mplu.set_axes_size(2.5, ax=ax)
