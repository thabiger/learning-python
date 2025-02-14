

def foo(b, a = [1, 2, 3]):
    a+=b
    return a

print(foo( [4,5,6] ))
print(foo( [3,2,1] ))