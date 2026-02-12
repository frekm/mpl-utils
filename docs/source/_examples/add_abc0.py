import matplotlib.pyplot as plt
import mplutils as mplu

fig, _ = plt.subplots(2, 3, layout="compressed")
mplu.add_abc()
fig.suptitle("add_abc(): Default")
plt.show()
