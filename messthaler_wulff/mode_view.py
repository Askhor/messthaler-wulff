import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import messthaler_wulff.objects as objects
from messthaler_wulff.objects import ObjectCollection
from messthaler_wulff.utils import convex_hull


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

def run_mode(initial, lattice, use_orthogonal_projections=False, show_axes=True):
    setup_matplotlib(use_orthogonal_projections=use_orthogonal_projections, show_axes=show_axes)

    points = [p[-3:] for p in initial]
    points = [np.dot(lattice, p) for p in points]
    points = ObjectCollection.from_points(*np.transpose(points))
    convex_hull(points).plot()

    show_matplotlib()
