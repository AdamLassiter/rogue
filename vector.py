#! /usr/bin/env python3


class vector(list):
    from types import GeneratorType as generator
    iterable = (tuple, list, generator)

    def __init__(self, *args):
        super().__init__(*args)
        assert len(self) == 3

    def __copy__(self):
        return self.__class__(tuple(self))

    def __or__(self, other):
        return vector(list(self) + list(other))

    def __eq__(self, other):
        if isinstance(other, vector.iterable):
            return all(map(lambda x, y: x == y, self, other))
        return False

    def __getitem__(self, sl):
        if isinstance(sl, slice):
            return vector(super().__getitem__(sl))
        else:
            return super().__getitem__(sl)

    def __add__(self, other):
        if isinstance(other, vector.iterable):
            return vector(map(lambda x, y: x + y, self, other))
        return vector(map(lambda x: x + other, self))

    def __iadd__(self, other):
        return self + other

    def __neg__(self):
        return vector(map(lambda x: -x, self))

    def __sub__(self, other):
        if isinstance(other, vector.iterable):
            return self + (-x for x in other)
        else:
            return self + other.__neg__()

    def __mul__(self, other):
        if isinstance(other, vector.iterable):
            return vector(map(lambda x, y: x * y, self, other))
        return vector(map(lambda x: x * other, self))

    def __truediv__(self, other):
        if isinstance(other, vector.iterable):
            return vector(map(lambda x, y: x / y, self, other))
        return vector(map(lambda x: x / other, self))

    def __floordiv__(self, other):
        if isinstance(other, vector.iterable):
            return vector(map(lambda x, y: x // y, self, other))
        return vector(map(lambda x: x // other, self))

    def __pow__(self, other):
        if isinstance(other, vector.iterable):
            return vector(map(lambda x, y: x ** y, self, other))
        return vector(map(lambda x: x // other, self))
