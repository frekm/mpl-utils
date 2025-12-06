import matplotlib.pyplot as plt
import mplutils as mplu

# set the figure size. Note that the figure width will be changed by add_colpad_pts
plt.rcParams["figure.figsize"] = 6.4, 12.0

# create axes and format ticks/ticklabels for illustration purposes
plt.subplot(311).set_xticklabels([])
plt.subplot(312)
plt.subplot(313).set_ylim(0, 10000)

# get extra space between columns and remove it
for irow in range(4):
    extra_space = mplu.get_row_pad_pts(irow, ignore_labels=False)
    mplu.add_row_pad_pts(irow, -extra_space)
