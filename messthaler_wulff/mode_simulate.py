# XDG_SESSION_TYPE=x11 for Linux

import random

import open3d as o3d

from .additive_simulation import SimpleNeighborhood, OmniSimulation
from .data import *
from .progress import ProgressBar


def plot_sim(sim, lattice):
    points = o3d.geometry.PointCloud()
    points.points = o3d.utility.Vector3dVector(np.asarray([np.dot(lattice, p[1:])
                                                           for p in sim.points()]))

    o3d.geometry.PointCloud(points)
    o3d.visualization.draw_geometries([points])


def run_mode(goal, lattice):
    simulation = OmniSimulation(SimpleNeighborhood(lattice), None, (0, 0, 0, 0))
    input("Press enter to continue...")

    p = ProgressBar(goal, lambda: simulation.energy)

    for i in range(goal):
        p(i)
        simulation.add_atom(lambda l: random.randrange(l))

    plot_sim(simulation, lattice)
