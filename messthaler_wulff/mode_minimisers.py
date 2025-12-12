import logging

from prettytable import PrettyTable

from messthaler_wulff.additive_simulation import OmniSimulation, SimpleNeighborhood, wipe_screen
from messthaler_wulff.minimiser_simulation import MinimiserSimulation

log = logging.getLogger("messthaler_wulff")


def show_results(energies, counts, intermediate_value=False):
    if intermediate_value:
        wipe_screen()
        print("Intermediate results:")
    else:
        print("Final results:")

    table = PrettyTable(["nr atoms", "nr crystals", "min energy"], align='r')
    table.custom_format = lambda f, v: f"{v:,}"

    for i in counts.keys():
        table.add_row([i, counts[i], energies[i]])

    print(table)


def run_mode(goal, lattice, dimension, dump_crystals):
    omni_simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (dimension + 1)))
    sim = MinimiserSimulation(omni_simulation)

    if dump_crystals:
        for m in sim.minimisers(goal):
            print(m.sim.omni_simulation)
    else:
        for n in range(goal + 1):
            print(f"{n:3}: {sim.data(n)}")
