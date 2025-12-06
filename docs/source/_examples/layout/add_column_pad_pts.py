import matplotlib.pyplot as plt
import mplutils as mplu

# set the figure size. Note that the figure width will be changed by add_colpad_pts
plt.rcParams["figure.figsize"] = 6.4, 2.0

# create axes and format ticks/ticklabels for illustration purposes
plt.subplot(131).set_xticklabels([])
plt.subplot(132).set_xlim(0, 10000)  # ticklabels reach into third column
plt.subplot(133)

# get extra space between columns and remove it
for icol in range(4):
    extra_space = mplu.get_column_pad_pts(icol)
    mplu.add_column_pad_pts(icol, -extra_space)
