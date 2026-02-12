import matplotlib.pyplot as plt

fig, axs = plt.subplots(3, 2, layout="compressed")
fig.set_facecolor("grey")

for ax in axs.flat:
    ax.set_box_aspect(1)
