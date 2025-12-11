import random

from .additive_simulation import SimpleNeighborhood, OmniSimulation
from .progress import ProgressBar


def run_mode(goal, dimension, lattice, windows_mode):
    simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (1 + dimension)))
    input("Press enter to continue...")

    p = ProgressBar(goal, lambda: simulation.energy)

    for i in range(goal):
        p(i)
        simulation.add_atom(lambda l: random.randrange(l))

    simulation.interactive(dimension, color=not windows_mode)
