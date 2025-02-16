import os
import random
import matplotlib.pyplot as plt
from collections import defaultdict

from c04_vectors_basics import Vector

def random_color():
    return (random.random(), random.random(), random.random())

class VisualVectorOperator:

    def __init__(self, ):
        plt.figure()
        plt.axvline(x=0, color='grey', lw=1)
        plt.axhline(y=0, color='grey', lw=1)

        self.lim = defaultdict(lambda: [0, 0])
        self.last_tail = Vector([0, 0])

    def add(self, vector):
        plt.quiver(*self.last_tail.dimensions, *vector.dimensions, angles='xy', scale_units='xy', scale=1, color=random_color())
        self.last_tail += vector
        self.update_plot_size()

    def sub(self, vector):
        self.add(vector * -1)

    def update_plot_size(self):
        # here i keep track of the min and max values for the x and y axis, to set appropriate limits for the plot
        for d in range(len(self.last_tail.dimensions)):
            self.lim[d] = min(self.lim[d][0], self.last_tail.dimensions[d]), max(self.lim[d][1], self.last_tail.dimensions[d])

    def solve(self):
        # resulting vector
        plt.quiver(*Vector([0, 0]).dimensions, *self.last_tail.dimensions, angles='xy', scale_units='xy', scale=1, color='white', linestyle=('--'), linewidth=0.4, edgecolor='black')

        plt.xlim(*self.lim[0])
        plt.ylim(*self.lim[1])
        plt.grid()
        plt.savefig(os.path.splitext(os.path.basename(__file__))[0])
        plt.close()

x = VisualVectorOperator()

x.add(Vector([10, 10]))
x.add(Vector([3, 24]))
x.add(Vector([3, -12]))
x.solve()