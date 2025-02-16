import math

class Vector:

    def __init__(self, dimensions: list):
        self.dimensions = dimensions

    def __add__(self, other):
        if len(self.dimensions) != len(other.dimensions):
            raise ValueError("Vectors must have the same dimensions")
        return Vector([ a + b for (a, b) in zip(self.dimensions, other.dimensions) ])

    def __sub__(self, other):
        if len(self.dimensions) != len(other.dimensions):
            raise ValueError("Vectors must have the same dimensions")
        return Vector([ a - b for (a, b) in zip(self.dimensions, other.dimensions) ])
    
    def __mul__(self, other):
        return Vector([a * other for a in self.dimensions])

    def dot(self, other):
        """ 
        The dot product of two vectors is the sum(a scalar value) of their componentwise products.

        It is useful in determining the angle between two vectors, projecting one vector onto another,
        and in various applications in physics and engineering
        
        If w has magnitude 1, the dot product measures how far the vector v extends in the w direction. For
        example, if w = [1, 0], then dot(v, w) is just the first component of v. Another way of saying this is
        that it’s the length of the vector you’d get if you projected v onto w
        """
        return sum([a * b for a, b in zip(self.dimensions, other.dimensions)])

    # a special case of the dot product, made on the vector itself
    def sum_of_squares(self):
        return self.dot(self)

    def magnitude(self):
        return math.sqrt(self.sum_of_squares())

    def distance(self, other):
        sum_of_squares = sum([(a - b) ** 2 for a, b in zip(self.dimensions, other.dimensions)])
        return math.sqrt(sum_of_squares)

    def multiply_scalar(self, scalar):
        return Vector([a * scalar for a in self.dimensions])

    def __len__(self):
        return len(self.dimensions)

    def __repr__(self):
        return "Vector([%s])" % ", ".join(map(str, self.dimensions))
     

# Function to add a list of vectors
def vector_sum(vectors):
    assert vectors, "At least one vector must be provided"
    
    # by default sum uses uses 0 a the start value; as it's not a valid vector, we use the first vector instead (vectors[0])
    return sum(vectors[1:], vectors[0])

def vector_mean(vectors):
    l = len(vectors)
    return (vector_sum([ v * (1/l) for v in vectors ]))

if __name__ == "__main__":

    v1 = Vector([1, 2, 3])
    v2 = Vector([4, 5, 6])
    v3 = Vector([7, 8, 9])

    print("Vectors sum: %s" % (v1 + v2 + v3))           # -> implemented by __add__
    print("Vectors substraction: %s" % (v1 - v2 - v3))  # -> implemented by __sub__
    print("Scalar multiplyig: %s" % (v1 * 3))           # -> implemented by __mul__
    print("Vectors mean: %s" % (vector_mean([v1, v2]))) # -> implemented by __mul__

    print("Vectors length: %s" % len(v1))               # -> implemented by __len__

    # vector sum function; use an __add__ buitlin method
    print("Vectors sum(alt.): %s" %vector_sum([v1, v2, v3]))
    # testing the assertion
    try:
        print(vector_sum([]))
    except AssertionError as e:
        print ("Arguments dont't meet the requirements:", e)

    # other products
    print("Vectors dot product: %s" % v1.dot(v2))
    print("Vector's sum of squares: %s" %v1.sum_of_squares())
    print("Vector's magnitude: %s" % v1.magnitude())
    print("Distance between vectors: %s" % v1.distance(v2))

