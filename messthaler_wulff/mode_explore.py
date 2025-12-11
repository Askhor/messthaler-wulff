import logging

from prettytable import PrettyTable

from messthaler_wulff.additive_simulation import OmniSimulation, SimpleNeighborhood, wipe_screen
from messthaler_wulff.explorative_simulation import crystal_data
from messthaler_wulff.progress import debounce

log = logging.getLogger("messthaler_wulff")


def show_results(energies, counts, intermediate_value=False):
    if intermediate_value:
        wipe_screen()
        print("Intermediate results:")
    else:
        print("Final results:")

    table = PrettyTable(["nr atoms", "nr crystals", "min energy"], align='r')

    for i in counts.keys():
        table.add_row([i, counts[i], energies[i]])

    print(table)


def run_mode(goal, lattice, dimension):
    omni_simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (dimension + 1)))

    energies, counts = crystal_data(omni_simulation, goal, debounce(lambda e,c: show_results(e,c, True)))

    show_results(energies, counts)
