import os
import matplotlib.pyplot as plt

from c04_vectors_basics import Vector

def plot_projection(a, b):
    plt.figure(figsize=(6, 6))
    ax = plt.gca()
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal', 'box')  # so that x and y scales are the same

    # draw the original vectors (from origin to their respective tips)
    origin = [0], [0]
    ax.quiver(*origin, *a.dimensions, angles='xy', scale_units='xy', scale=1, color='red', label='Vector a')
    ax.quiver(*origin, *b.dimensions, angles='xy', scale_units='xy', scale=1, color='blue', label='Vector b')

    # calculate the projection of a onto b
    proj_of_a_on_b = b * (a.dot(b) / b.sum_of_squares())

    ax.quiver(*origin, *proj_of_a_on_b.dimensions,
            angles='xy', scale_units='xy', scale=1, color='green', label='Proj of a on b')

    # draw a dashed line from the tip of the projection to the tip of a
    #   to visually show the "difference" (the perpendicular component)
    ax.plot([proj_of_a_on_b.dimensions[0], a.dimensions[0]], [proj_of_a_on_b.dimensions[1], a.dimensions[1]], 'k--', label='Difference')

    # add labels and a legend
    plt.title('Visualizing Vector Projection')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.grid(True)

    plt.savefig(os.path.splitext(os.path.basename(__file__))[0])

    # Print some helpful info
    print(f"Vector a = {a}")
    print(f"Vector b = {b}")
    print(f"Projection of a onto b = {proj_of_a_on_b}")

if __name__ == "__main__":

    plot_projection(Vector([3, 1]), Vector([2, 1.5]))