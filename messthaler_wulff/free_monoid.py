import random


class FreePrimitive:
    primitives = {}
    extended_to_string = False

    def __init__(self, length: int, first, last, part_a: 'FreePrimitive', part_b: 'FreePrimitive'):
        assert length > 0
        assert length - 1 & length == 0  # Is power of two

        self.id = random.randint(0, 1 << 31)
        self.length = length
        self.first = first
        self.last = last
        self.part_a = part_a
        self.part_b = part_b
        self.next = {}

    @classmethod
    def wrap_primitive(cls, primitive):
        if primitive in cls.primitives:
            return cls.primitives[primitive]

        value = cls(1, primitive, primitive, None, None)
        cls.primitives[primitive] = value
        return value

    def __hash__(self):
        return self.id

    def __eq__(self, other: 'FreePrimitive'):
        return self is other

    def __len__(self):
        return self.length

    def __add__(self, other: 'FreePrimitive'):
        assert other.length >= self.length

        if other in self.next:
            return self.next[other]

        if self.length == other.length:
            new_next = FreePrimitive(self.length + other.length,
                                     self.first,
                                     other.last,
                                     self,
                                     other)
        elif 2 * self.length == other.length:
            new_next = (self + other.part_a, other.part_b)
        else:
            new_next = join(self + other.part_a, other.part_b)

        self.next[other] = new_next
        return new_next

    def double(self, n: int = 1):
        x = self
        for i in range(n):
            x = x + x
        return x

    def __mul__(self, other: int):
        x = self
        s = list()

        while other > 0:
            if other & 1:
                join_into(s, x)
            other >>= 1
            x = x.double()

        return tuple(s)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.length == 1:
            return str(self.first)
        elif self.extended_to_string:
            return str(self.part_a) + ":" + str(self.part_b)
        else:
            return str(self.part_a) + str(self.part_b)


def reduce_right(l: list[FreePrimitive]):
    while len(l) >= 2 and l[-2].length <= l[-1].length:
        right = l.pop()
        left = l.pop()
        s = left + right
        if isinstance(s, FreePrimitive):
            l.append(s)
        else:
            a, b = s
            l.append(a)
            reduce_right(l)
            l.append(b)


def join_into(a: list[FreePrimitive], b: tuple[FreePrimitive]):
    if isinstance(b, FreePrimitive):
        a.append(b)
        reduce_right(a)
        return

    for p in b:
        a.append(p)
        reduce_right(a)


def join(a: tuple[FreePrimitive], b: tuple[FreePrimitive]):
    if isinstance(a, FreePrimitive):
        a = (a,)
    out = list(a)
    join_into(out, b)
    return tuple(out)


def reduce(a: tuple[FreePrimitive]) -> tuple[FreePrimitive]:
    if isinstance(a, FreePrimitive):
        return a
    out = list()
    for c in a:
        join_into(out, c)
    return tuple(out)


def from_string(string: str):
    return reduce(map(FreePrimitive.wrap_primitive, string))


def monoid_length(a: tuple[FreePrimitive]) -> int:
    s = 0
    for p in a:
        s += p.length
    return s


def is_correct_monoid(a: tuple[FreePrimitive]) -> bool:
    if len(a) == 0: return True
    if not isinstance(a[0], FreePrimitive):
        return False

    for i in range(len(a) - 1):
        if not isinstance(a[i + 1], FreePrimitive):
            return False
        if not a[i].length > a[i + 1].length:
            return False

    return True


def rexlca(a: tuple[FreePrimitive], b: tuple[FreePrimitive]):
    if isinstance(a, FreePrimitive):
        a = [a]
    else:
        a = list(a)
    if isinstance(b, FreePrimitive):
        b = [b]
    else:
        b = list(b)

    def split_last(l: list):
        x1 = l[-1].part_a
        x2 = l.pop().part_b
        l.append(x1)
        l.append(x2)

    out = list()

    while True:
        if len(a) == 0 or len(b) == 0:
            break
        elif a[-1] == b[-1]:
            join_into(out, a.pop())
            b.pop()
        elif a[-1].length == 1 and b[-1].length == 1:
            break
        elif a[-1].length == b[-1].length:
            split_last(a)
            split_last(b)
        elif a[-1].length > b[-1].length:
            split_last(a)
        else:
            split_last(b)

    reduce_right(a)
    reduce_right(b)
    return tuple(reversed(out)), tuple(a), tuple(b)


def insert(a: tuple[FreePrimitive], b: FreePrimitive) -> tuple[FreePrimitive]:
    if isinstance(a, FreePrimitive):
        a = [a]

    element = b.first

    out = list(a)
    i = 0

    while True:
        if i >= len(out):
            join_into(out, b)
            return tuple(out)
        elif element <= out[i].first:
            out.insert(i, b)
            return reduce(out)
        elif element > out[i].last:
            i += 1
        else:
            value = out[i]
            out[i] = value.part_a
            out.insert(i + 1, value.part_b)


def remove(a: tuple[FreePrimitive], element) -> tuple[FreePrimitive]:
    if isinstance(a, FreePrimitive):
        a = [a]

    out = list(a)
    i = 0

    while True:
        if i >= len(out) or element < out[i].first:
            raise ValueError(f"Primitive {element} was not present in {a}")
        elif element > out[i].last:
            i += 1
        elif out[i].length == 1:
            assert out[i].first == element
            del out[i]
            return reduce(out)
        else:
            value = out[i]
            out[i] = value.part_a
            out.insert(i + 1, value.part_b)
