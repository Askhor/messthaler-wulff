import math

from scipy.spatial import ConvexHull, Voronoi

from .objects import *

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


def ngon(n):
    angles = np.arange(0, n) / n * 2 * np.pi

    return ObjectCollection.from_points(
        np.cos(angles),
        np.sin(angles),
        [0] * n
    )


def vector_length(vector):
    return math.sqrt(np.dot(vector, vector))


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


def auto_lines(oc: ObjectCollection, length):
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


def grid(x_values, y_values, z_values):
    """
    Given the three parameter sets X,Y,Z, generates X×Y×Z
    """
    points = []

    for x in x_values:
        for y in y_values:
            for z in z_values:
                points.append(Point(np.array([x, y, z])))

    return ObjectCollection(points)


def points_inward(triangle, center):
    """
    A utility method to define whether a triangle is pointing towards the center of some convex polygon
    """
    a = triangle[1] - triangle[0]
    b = triangle[2] - triangle[0]
    orth = np.cross(a, b)

    return np.dot(orth, center - triangle[0]) > 0


def types_of_iterable(itr):
    return list(map(type, itr))


def convex_hull(points: ObjectCollection):
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


def voronoi(points: ObjectCollection, position: np.ndarray, length):
    neighbors = [p.pos for p in points.get_points() if distance_matches(position, p.pos, length)]

    _voronoi = Voronoi([*neighbors, position])

    return convex_hull(ObjectCollection([Point(v) for v in _voronoi.vertices]))


def circum_sphere(points: ObjectCollection, detail: int = 100):
    coords = list(map(lambda p: p.pos, points.get_points()))
    center = sum(coords) * (1 / len(coords))
    radius = max(vector_length(v - center) for v in coords)

    return points @ ObjectCollection([Sphere(center, radius, detail=detail)])


def constant(fun):
    """
    A utility decorator, to make code faster, does not change behaviour
    """
    value = fun()
    return lambda: value


def setter(name, value):
    """
    Returns a function that takes an object and sets the 'name' field to 'value'
    """

    def s(x):
        x.__setattr__(name, value)

    return s
