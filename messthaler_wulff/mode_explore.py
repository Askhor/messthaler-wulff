import logging

from prettytable import PrettyTable

from messthaler_wulff.additive_simulation import OmniSimulation, SimpleNeighborhood
from messthaler_wulff.explorative_simulation import ExplorativeSimulation
from messthaler_wulff.simulation_state import SimpleCrystalHasher, TICrystalHasher

log = logging.getLogger("messthaler_wulff")


def show_results(energies, counts):
    table = PrettyTable(["nr atoms", "nr crystals", "min energy"], align='r')
    table.custom_format = lambda f, v: f"{v:,}"

    for i in range(len(counts)):
        table.add_row([i, counts[i], energies[i]])

    print(table)


def run_mode(goal, lattice, dimension, dump_crystals):
    omni_simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (dimension + 1)))
    explorer = ExplorativeSimulation(omni_simulation, TICrystalHasher(dimension))

    for n in range(goal + 1):
        log.debug(f"{n:3}: {explorer.min_energy(n):4} {explorer.crystal_count(n):10}")

    if dump_crystals:
        for state in explorer.crystals(goal):
            if state.energy == explorer.min_energy(goal):
                print(state.as_list())
    else:
        show_results([explorer.min_energy(n) for n in range(goal + 1)],
                     [explorer.crystal_count(n) for n in range(goal + 1)])
