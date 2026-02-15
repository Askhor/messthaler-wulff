import logging
import random

from ._additive_simulation import SimpleNeighborhood, OmniSimulation
from .progress import ProgressBar

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


def run_mode(goal, dimension, lattice, windows_mode, initial):
    simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (1 + dimension)))
    for atom in initial:
        simulation.force_set_atom(atom, OmniSimulation.FORWARDS)

    input("Press enter to continue...")

    p = ProgressBar(goal, lambda: simulation.energy)

    for i in range(goal):
        p(i)
        simulation.add_atom(lambda l: random.randrange(l))

    simulation.interactive(dimension, color=not windows_mode)
