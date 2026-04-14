import math

from scipy.spatial import ConvexHull

log = logging.getLogger("messthaler_wulff")


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
