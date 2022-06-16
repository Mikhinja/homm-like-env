#import numpy as np

# example on how to debug A* on a grid:

import matplotlib.pyplot as plt
before = {} # get value from debug: came_from -> dict mapping adjacent positions. tip: use print(came_from) in debug console, otherwise it will get truncated
XB = [before[p][0] for p in before]
YB = [before[p][1] for p in before]
UB = [p[0]-before[p][0] for p in before]
VB = [p[1]-before[p][1] for p in before]
plt.quiver(XB, YB, UB, VB, color='r')
plt.title('before bad')
plt.xlim(-1, 39)
plt.ylim(-1, 39)
plt.grid()
plt.show()

# for profiling:  python -m cProfile -o train_test.stats train.py
# to investigate: python -m pstats train_test.stats