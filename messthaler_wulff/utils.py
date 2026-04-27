import math
import random
from collections import defaultdict
from typing import Optional

from scipy.spatial import ConvexHull


def unordered_remove[T](lst: list[T], index: int) -> None:
    assert 0 <= index < len(lst)

    last = lst.pop()

    if index != len(lst):
        lst[index] = last


class setr[T]:
    def __init__(self) -> None:
        self.list: list[T] = []
        self.map: dict[T, int] = {}

    def __len__(self) -> int:
        return len(self.list)

    def add(self, el: T) -> None:
        if el in self.map: return

        self.map[el] = len(self.list)
        self.list.append(el)

    def remove(self, el: T) -> None:
        assert el in self.map
        index = self.map.pop(el)
        assert 0 <= index < len(self.list)
        assert self.list[index] == el

        last = self.list.pop()
        if index == len(self.list):  # If the element is the last in the list
            ...
        else:
            self.list[index] = last
            self.map[last] = index

    def random(self) -> T:
        return random.choice(self.list)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.list)


def psi(x: int) -> int:
    return 2 * x - 1


class priority_stack[T]:
    MIN = 0
    MAX = 1

    def __init__(self) -> None:
        self.levels: defaultdict[int, setr[T]] = defaultdict(setr)
        self.priorities: dict[T, int] = {}
        self.bounds: list[Optional[int]] = [None, None]

    def __len__(self) -> int:
        return len(self.priorities)

    def set(self, el: T, priority: int) -> None:
        old_min = self.bounds[self.MIN]
        old_max = self.bounds[self.MAX]
        if old_min is None or priority < old_min:
            self.bounds[self.MIN] = priority
        if old_max is None or priority > old_max:
            self.bounds[self.MAX] = priority

        if el in self.priorities:
            self.levels[self.priorities[el]].remove(el)

        self.priorities[el] = priority
        self.levels[priority].add(el)

        self.contract_bounds()

    def unset(self, el: T) -> None:
        if el not in self.priorities:
            return

        self.levels[self.priorities[el]].remove(el)
        del self.priorities[el]

        if len(self) > 0:
            self.contract_bounds()
        else:
            self.bounds[0] = None
            self.bounds[1] = None

    def contract_bound(self, bound: int) -> None:
        s = psi(bound)
        current = self.bounds[bound]

        while current not in self.levels or len(self.levels[current]) == 0:
            current -= s

        self.bounds[bound] = current

    def contract_bounds(self) -> None:
        self.contract_bound(self.MIN)
        self.contract_bound(self.MAX)

    def min(self) -> setr[T]:
        assert self.bounds[self.MIN] is not None
        return self.levels[self.bounds[self.MIN]]

    def max(self) -> setr[T]:
        assert self.bounds[self.MAX] is not None
        return self.levels[self.bounds[self.MAX]]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.bounds[self.MIN]} ≤ {dict(self.levels)} ≤ {self.bounds[self.MAX]}"


def clamp(x, _min, _max):
    if x < _min: return _min
    if x > _max: return _max

    return x


def clamped_line(x1, y1, x2, y2, x):
    slope = (y2 - y1) / (x2 - x1)
    raw_value = slope * (x - x1) + y1
    return clamp(raw_value, min(y1, y2), max(y1, y2))


def wipe_screen():
    print(end=clear_screen(2) + clear_screen(3) + Cursor.POS(0, 0), flush=True)


def call_by_getitem(function):
    class impl:
        def __getitem__(self, i):
            return function(i)

        def __call__(self, *args, **kwargs):
            return function(*args, **kwargs)

    return impl()


def distance_matches(a, b, length):
    distance = vector_length(np.subtract(a, b))

    return math.isclose(distance, length)


def np_auto_lines(points, length):
    edges = []

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if distance_matches(points[i], points[j], length):
                edges.append(Line(points[i], points[j]))

    return ObjectCollection(edges)


def auto_lines(oc, length):
    """
    Generates a new Object with lines added between points of distance 'length'
    """
    objs = oc.objs
    edges = []

    for i in range(len(objs)):
        a = objs[i]
        if not isinstance(a, Point):
            continue
        for j in range(i + 1, len(objs)):
            b = objs[j]
            if not isinstance(b, Point):
                continue

            if distance_matches(a.pos, b.pos, length):
                edges.append(Line(a.pos, b.pos))

    return oc @ ObjectCollection(edges)


def convex_hull(points):
    """
    Given an ObjectCollection returns the polygon that is the convex hull
    """
    point_coords = []

    for o in points.objs:
        if not isinstance(o, Point): continue
        point_coords.append(o.pos)

    center = sum(point_coords) / len(point_coords)

    ch = ConvexHull(np.array(point_coords))
    triangles = []

    for a, b, c in ch.simplices:
        tri = [point_coords[a],
               point_coords[b],
               point_coords[c]]

        if points_inward(tri, center):
            tri.reverse()

        triangles.append(Triangle(*tri))

    return ObjectCollection(triangles)
