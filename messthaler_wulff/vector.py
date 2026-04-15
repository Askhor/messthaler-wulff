from functools import singledispatchmethod


class vec:
    def __init__(self, value: tuple):
        self.value: tuple = value

    @classmethod
    def new(cls, *values: int):
        return cls(tuple(values))

    @classmethod
    def zero(cls, dim: int):
        return cls(tuple([0] * dim))

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item: int):
        return self.value[item]

    def __iter__(self):
        return iter(self.value)

    def __neg__(self):
        return -1 * self

    @singledispatchmethod
    def __add__(self, other):
        raise NotImplementedError(f"Cannot add {type(self)} to {type(other)}")

    @singledispatchmethod
    def __mul__(self, other):
        raise NotImplementedError(f"Cannot multiply {type(self)} with {type(other)}")

    def __sub__(self, other):
        return self + (-other)

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other

    def __rsub__(self, other):
        return self - other

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, vec) and self.value == other.value


@vec.__add__.register
def _(a, b: vec):
    assert len(a) == len(b)
    return vec.new(*(a[i] + b[i] for i in range(len(a))))


@vec.__mul__.register
def _(a, b: int):
    return vec.new(*(b * a[i] for i in range(len(a))))
