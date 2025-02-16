from typing import List, Callable

from c04_vectors_basics import Vector

class Matrix:

    """
     What they're useful for? Representing:
        - data sets
        - linear functions between vectors (a linear functions that maps k-dimensional
            vectors to n-dimensional vectors)
        - binary relationships (a matrix with 1s and 0s); amore effective equiv of representing
          the edges of a network(graph) as a list of pairs
    """

    def __init__(self, matrix: List[List[int | float]]) -> None:
        self.matrix = matrix

    def shape(self):
        num_rows = len(self.matrix)
        num_cols = len(self.matrix[0])
        return num_rows, num_cols
    
    """
        for a n x k matrix:
         - a row is defined as a vector of length k
         - a coloumn as a vector of length n
    """
    def get_row(self, i: int) -> Vector: 
        return self.matrix[i]
    
    def get_column(self, j: int) -> Vector: 
        return[ row[j] for row in self.matrix ]
    
    def __repr__(self):
        return "Matrix(%s)" % self.matrix

    def __str__(self):
        return '\n'.join(['\t'.join(map(str, row)) for row in self.matrix])

def make_matrix(num_rows: int, num_cols: int, entry_fn: Callable[[int, int], int | float] | None = None) -> Matrix:
    
    def def_entry_fn():
        c = 0
        def increment(*args):
            nonlocal c
            c += 1
            return c
        return increment
    
    entry_fn = entry_fn if entry_fn else def_entry_fn()
    
    return (Matrix([[entry_fn(i, j) for j in range(num_cols)] for i in range(num_rows)]))


def make_identity_matrix(n: int) -> Matrix:
    return make_matrix(n, n, lambda i, j: 1 if i == j else 0)


if __name__ == "__main__":

    A = Matrix([[1, 2, 3], 
                [4, 5, 6], 
                [7, 8, 9]]
                )

    B = Matrix([[1, 2],
                [3, 4], 
                [5, 6]]
                )

    print ("Matrix A shape: (%s,%s)" % A.shape())
    print ("Matrix B shape: (%s,%s)" % B.shape())

    print ("Matrix A row 1: %s" % A.get_row(1))
    print ("Matrix A column 1: %s" % A.get_column(1))

    print("Making matrix: %s" % make_matrix(3,3))
    print("Making identity matrix: %s" % make_identity_matrix(3))