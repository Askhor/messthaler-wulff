import logging

from prettytable import PrettyTable

from messthaler_wulff.additive_simulation import OmniSimulation, SimpleNeighborhood
from messthaler_wulff.explorative_simulation import ExplorativeSimulation

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


def show_results(energies, counts):
    table = PrettyTable(["nr atoms", "nr crystals", "min energy"], align='r')
    table.custom_format = lambda f, v: f"{v:,}"

    for i in range(len(counts)):
        table.add_row([i, counts[i], energies[i]])

    print(table)


def compare_hash_functions(goal, dump_crystals, ex1, ex2):
    if dump_crystals:
        a = frozenset(c.as_list() for c in ex1.crystals(goal))
        b = frozenset(c.as_list() for c in ex2.crystals(goal))
        if a == b:
            log.info("No difference")
        else:
            log.info(a - b)
            log.info(b - a)
        return

    for n in range(goal + 1):
        log.debug(f"Checking {n}")
        v1 = ex1.relevant_data(n)
        v2 = ex2.relevant_data(n)

        if v1 != v2:
            log.error(f"For n={n}: {v1} != {v2}")

    log.info("Done")


def run_mode(goal, lattice, dimension, dump_crystals, hash_function, compare_hash_function=None):
    omni_simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (dimension + 1)))
    explorer = ExplorativeSimulation(omni_simulation, hash_function[0], hash_function[1])

    if compare_hash_function is not None:
        omni_simulation2 = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (dimension + 1)))
        explorer2 = ExplorativeSimulation(omni_simulation2, compare_hash_function[0], compare_hash_function[1])

        compare_hash_functions(goal, dump_crystals, explorer, explorer2)
        return

    for n in range(goal + 1):
        log.debug(f"{n:3}: {explorer.min_energy(n):4} {explorer.crystal_count(n):10}")

    if dump_crystals:
        for state in explorer.crystals(goal):
            if state.energy == explorer.min_energy(goal):
                print(state.as_list())
    else:
        show_results([explorer.min_energy(n) for n in range(goal + 1)],
                     [explorer.crystal_count(n) for n in range(goal + 1)])
