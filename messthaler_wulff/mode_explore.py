import logging

from messthaler_wulff.additive_simulation import OmniSimulation, SimpleNeighborhood
from messthaler_wulff.explorative_simulation import ExplorativeSimulation

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


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


def crystal_file_name(dimension, count, gm_mode, bidi, ti):
    mode = ""
    if gm_mode:
        mode += "g"
    if bidi:
        mode += "b"
    if ti:
        mode += "t"
    return f"Crystals in {dimension}d with {count} atoms (mode: {mode}).txt"


def run_mode(goal, lattice, dimension, dump_crystals=None, verbose=False, initial=None,
             gm_mode=False, ti=True, bidi=True):
    omni_simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (dimension + 1)))
    for atom in initial:
        omni_simulation.force_set_atom(atom, OmniSimulation.FORWARDS)
    explorer = ExplorativeSimulation(omni_simulation, goal, verbose=verbose,
                                     gm_mode=gm_mode, ti=ti, bidi=bidi, collect_crystals=dump_crystals)

    print(explorer)

    if dump_crystals:
        for i in range(explorer.lower_bound, explorer.upper_bound + 1):
            d = explorer.data_index(i)
            file = dump_crystals / crystal_file_name(dimension, i, gm_mode, bidi, ti)
            if file.exists():
                log.error(f"File {file} already exists")
                continue
            file.write_text(("\n".join("["
                                       + ", ".join(map(str, c.atoms()))
                                       + "]"
                                       for c in explorer.crystals[d])))
