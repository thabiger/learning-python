
import os
import networkx as nx
import matplotlib.pyplot as plt

from c04_matrices_basics import *

### There are 9 people. Each pair is representing a friendship between them.
friendships = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (5, 7), (6, 8), (7, 8), (8, 9)]

# I'd like to represent the same data using a matrix
# First, I need to know the shape of the matrix
max_id = max([max(pair) for pair in friendships]) + 1 #max_id is actually 9; but in python we're counting from 0, so that gives us 10 people

m = make_matrix(max_id, max_id, lambda i, j: 1 if (i, j) in friendships or (j, i) in friendships else 0)
print(m)

# now, friendships can be easily checked without iterating over a list of pairs
print ("Are 1 and 2 friends? %s" % bool(m.get_row(1)[2]))
print ("Are 4 and 9 friends? %s" % bool(m.get_row(4)[9]))

# on the other hand, when trying to make the relationships graph, having a list of pairs occured to be more convenient

G = nx.Graph()
# Add nodes...
G.add_nodes_from(range(max_id))
# ... and edges
for i,j in friendships:
    G.add_edge(i, j)

# Draw the graph
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500, font_size=10)
plt.savefig(os.path.splitext(os.path.basename(__file__))[0])
plt.close()
