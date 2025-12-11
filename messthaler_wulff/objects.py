from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import numpy.linalg as la

ax = None


def square_repeat(array, axis):
    shp = (np.size(array), 1) if axis == 0 else (1, np.size(array))
    return np.repeat(np.reshape(array, shp), np.size(array), axis=1 - axis)


class Object(ABC):
    def __init__(self):
        self.color = "grey"
        self.always_on_top = False
        self.opacity = 1
        self.style = ''

    @abstractmethod
    def __mul__(self, matrix):
        pass

    @abstractmethod
    def __add__(self, vector):
        pass

    @abstractmethod
    def plot(self):
        pass

    @abstractmethod
    def predicate(self, p) -> bool:
        pass


class Point(Object):

    def __init__(self, pos):
        super().__init__()
        if not isinstance(pos, np.ndarray):
            raise ValueError(f"The position of points must be a nd array and not {type(pos)}")
        self.style = 'o'
        self.size = 10
        self.pos = pos

    def __mul__(self, matrix):
        return self.__class__(np.dot(matrix, self.pos))

    def __add__(self, vector):
        return self.__class__(np.add(self.pos, vector))

    def plot(self):
        kwargs = {
            'marker': self.style,
            'c': self.color,
            'linestyle': '',
            'markersize': self.size
        }
        if self.always_on_top:
            kwargs['zorder'] = 1000
        plt.plot(*self.pos, **kwargs)

    def predicate(self, p) -> bool:
        return p(self.pos)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return tuple(self.pos) == tuple(other.pos)

    def __hash__(self):
        return hash(tuple(self.pos))


class Line(Object):
    def __init__(self, a, b):
        super().__init__()
        self.style = '-'
        self.width = 1
        self.a = a
        self.b = b

    def __mul__(self, matrix):
        self.__class__(
            np.dot(matrix, self.a),
            np.dot(matrix, self.b))

    def __add__(self, vector):
        self.__class__(
            np.add(vector, self.a),
            np.add(vector, self.b))

    def plot(self):
        kwargs = {
            'marker': '',
            'c': self.color,
            'linestyle': self.style,
            'linewidth': self.width,
            'alpha': self.opacity
        }
        if self.always_on_top:
            kwargs['zorder'] = 1000

        plt.plot(*np.transpose(np.array([self.a, self.b])), **kwargs)

    def predicate(self, p) -> bool:
        return p(self.a) and p(self.b)


class Triangle(Object):

    def __init__(self, a, b, c):
        super().__init__()
        self.c = c
        self.b = b
        self.a = a

    def __mul__(self, matrix):
        return self.__class__(
            np.dot(matrix, self.a),
            np.dot(matrix, self.b),
            np.dot(matrix, self.c))

    def __add__(self, vector):
        return self.__class__(
            np.add(vector, self.a),
            np.add(vector, self.b),
            np.add(vector, self.c))

    def plot(self):
        kwargs = {
            'color': self.color,
            'edgecolor': self.color,
            'linewidth': 0,
            'antialiased': True,
            'shade': True,
            'alpha': self.opacity
        }
        if self.always_on_top:
            kwargs['zorder'] = 10000

        x, y, z = np.transpose(np.array([self.a, self.b, self.c]))
        ax.plot_trisurf(
            x, y, [[0, 1, 2]], z,
            **kwargs)

    def predicate(self, p) -> bool:
        return p(self.a) and p(self.b) and p(self.c)


class Sphere(Object):
    def __init__(self, center, radius: float, detail: int = 100):
        super().__init__()
        self.center = center
        self.radius = radius
        self.detail = detail

    def __mul__(self, matrix):
        return self.__class__(np.dot(matrix, self.center), la.det(matrix) * self.radius, self.detail)

    def __add__(self, vector):
        return self.__class__(np.add(self.center, vector), self.radius, self.detail)

    def plot(self):
        u = square_repeat(np.linspace(0, 2 * np.pi, self.detail), 0)
        v = square_repeat(np.linspace(-np.pi / 2, np.pi / 2, self.detail), 1)
        h = np.sin(v)
        r = self.radius * np.sqrt(square_repeat(np.repeat(1, self.detail), 0) - np.square(h))
        offset = np.repeat(np.reshape(self.center, (3, 1)), self.detail, axis=1)

        ax.plot_surface(
            r * np.cos(u) + offset[0],
            r * np.sin(u) + offset[1],
            self.radius * h + offset[2],
            alpha=self.opacity
        )

    def predicate(self, p) -> bool:
        return p(self.center)


class ObjectCollection(Object):
    """
    An arbitrary collection of Object instances
    """

    def __init__(self, objs):
        super().__init__()
        self.objs = objs

    def __mul__(self, matrix):
        new_objs = []
        for o in self.objs:
            new_objs.append(o * matrix)

        return self.__class__(new_objs)

    def __add__(self, vector):
        new_objs = []
        for o in self.objs:
            new_objs.append(o + vector)

        return self.__class__(new_objs)

    def __matmul__(self, other):
        return self.__class__(self.objs + other.objs)

    def plot(self):
        for o in self.objs:
            o.plot()

    def predicate(self, p) -> bool:
        for o in self.objs:
            if not p(o):
                return False
        return True

    @staticmethod
    def from_points(x, y, z):
        objs = []
        for pos in zip(x, y, z):
            objs.append(Point(np.array(pos)))
        return ObjectCollection(objs)

    def filter(self, p):
        new_objs = []

        for o in self.objs:
            if o.predicate(p):
                new_objs.append(o)

        return self.__class__(new_objs)

    def foreach(self, _type, fun):
        for o in self.objs:
            if isinstance(o, _type):
                fun(o)
        return self

    def get_points(self):
        points = set()
        self.foreach(Point, lambda p: points.add(p))
        return points
