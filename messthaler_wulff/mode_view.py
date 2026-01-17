import logging
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import messthaler_wulff.objects as objects
from messthaler_wulff.objects import ObjectCollection
from messthaler_wulff.utils import convex_hull, auto_lines

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")

################################################################################
# Some very technical configuration

def setup_matplotlib(use_orthogonal_projections=False, show_axes=True, elevation=30, azimuth=60, roll=0):
    matplotlib.rcParams["savefig.directory"] = "./examples"
    objects.ax = plt.figure().add_subplot(projection='3d')
    objects.ax.set_proj_type('ortho' if use_orthogonal_projections else 'persp')
    objects.ax.set_xlabel('X')
    objects.ax.set_ylabel('Y')
    objects.ax.set_zlabel('Z')

    if not show_axes:
        plt.axis('off')  # This line turns the axis off

    # objects.ax.dist = 5
    # objects.ax.view_init(elev=elevation, azim=azimuth, roll=roll)


def show_matplotlib():
    objects.ax.set_aspect('equal', share=True)
    plt.show()


################################################################################
# Config done

def run_mode(initial, lattice, use_orthogonal_projection=False, show_axes=True, show_points=True, line_length=None,
             show_convex_hull=True):
    setup_matplotlib(use_orthogonal_projections=use_orthogonal_projection, show_axes=show_axes)

    if len(initial) <= 0:
        log.error("Must provide at least one point")
        sys.exit(1)

    points = [p[-3:] for p in initial]
    points = [np.dot(lattice, p) for p in points]
    points = ObjectCollection.from_points(*np.transpose(points))

    result = ObjectCollection.from_points([],[],[])

    if show_points:
        result @= points
    if line_length is not None:
        result @= auto_lines(points, line_length)
    if show_convex_hull:
        result @= convex_hull(points)

    result.plot()

    show_matplotlib()
