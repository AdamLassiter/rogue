#! /usr/bin/python3

class vector(list):

    def __or__(self, other):
        return vector(list(self) + list(other))

    def __eq__(self, other):
        if isinstance(other, vector):
            return all(map(lambda x, y: x == y, self, other))
        return False

    def __add__(self, other):
        if isinstance(other, vector):
            return vector(map(lambda x, y: x + y, self, other))
        return vector(map(lambda x: x + other, self))

    def __iadd__(self, other):
        return self + other

    def __neg__(self):
        return vector(map(lambda x: -x, self))

    def __sub__(self, other):
        return self + other.__neg__()

    def __mul__(self, other):
        if isinstance(other, vector):
            return vector(map(lambda x, y: x * y, self, other))
        return vector(map(lambda x: x * other, self))

    def __truediv__(self, other):
        if isinstance(other, vector):
            return vector(map(lambda x, y: x / y, self, other))
        return vector(map(lambda x: x / other, self))

    def __floordiv__(self, other):
        if isinstance(other, vector):
            return vector(map(lambda x, y: x // y, self, other))
        return vector(map(lambda x: x // other, self))

    def __pow__(self, other):
        if isinstance(other, vector):
            return vector(map(lambda x, y: x ** y, self, other))
        return vector(map(lambda x: x // other, self))
