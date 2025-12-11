from data import *


################################################################################
# The definitions of the fcc, hcp, etc. methods

def fcc(grid_range=range(0, 4), lower_bound=0, upper_bound=1.9, upper_clip_plane=math.inf, add_lines=True):
    """
    Generates a subset of fcc
    :grid_range: The range for the grid which will be range(-3,4) × range(-3,4) × range(-3, 4)
    """
    g = grid(grid_range, grid_range, grid_range)
    g *= fcc_transform()
    g = g.filter(lambda p: all(lower_bound <= t <= upper_bound for t in p))
    g = g.filter(lambda p: sum(p[i] for i in range(3)) <= upper_clip_plane)
    if add_lines:
        g = auto_lines(g, 1)
    return g


def fcc_wulff(opacity=1, corner_color='red', color='darkred'):
    """
    Generates the polygon that is the wulff crystal (with side length 1)
    """
    wulff = fcc_wulff_obj()
    # wulff += pos(0,0,0)  # center the crystal (somewhat)
    wulff.foreach(Point, setter('color', corner_color))
    wulff = convex_hull(wulff)
    wulff.foreach(Triangle, setter('color', color))
    wulff.foreach(Triangle, setter('opacity', opacity))
    return wulff


def fcc_wulff2(opacity=1, corner_color='red', color='darkred'):
    """
    Generates the polygon that is the wulff crystal (with side length 2)
    """
    wulff = fcc_wulff2_obj()
    wulff.foreach(Point, setter('color', corner_color))
    wulff = convex_hull(wulff)
    wulff.foreach(Triangle, setter('color', color))
    wulff.foreach(Triangle, setter('alpha', opacity))
    return wulff


def hcp(grid_range=range(0, 4), lower_bound=0, upper_bound=1.9, upper_clip_plane=math.inf, custom_filter=lambda p: True,
        add_lines=True):
    """
    Generates a subset of hcp
    """

    g = grid(grid_range, grid_range, grid_range)
    g *= hcp_transform()
    g @= g + hcp_vector()
    g = g.filter(lambda p: all(lower_bound <= t <= upper_bound for t in p))
    g = g.filter(lambda p: sum(p[i] for i in range(3)) <= upper_clip_plane)
    g = g.filter(custom_filter)
    if add_lines:
        g = auto_lines(g, 1)
    return g


def print_point_set(s):
    """
    Given a set s consisting of Point instances, prints their positions
    """
    print(f"{len(s)} elements: ", *map(lambda p: p.pos, s))
