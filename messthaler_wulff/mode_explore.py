import logging
import os
from pathlib import Path

from messthaler_wulff.additive_simulation import OmniSimulation, SimpleNeighborhood
from messthaler_wulff.explorative_simulation import ExplorativeSimulation
from messthaler_wulff.terminal_formatting import wipe_screen

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


def crystal_file_name(dimension, count, require_energy, bidi, ti, initial, comparison):
    mode = ""
    if bidi:
        mode += "b"
    if ti:
        mode += "t"
    if require_energy is not None:
        mode += str(require_energy)
    if initial is not None:
        mode += f"i{len(initial)}"
    if comparison is not None:
        mode += f"c{comparison}"
    return f"Crystals in {dimension}d with {count} atoms (mode: {mode}).txt"


def run_mode(goal, lattice, dimension: int, dump_crystals=None, verbose=False, initial=None,
             require_energy=None, ti=True, bidi=True):
    omni_simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (dimension + 1)))
    for atom in initial:
        omni_simulation.force_set_atom(atom, OmniSimulation.FORWARDS)
    explorer = ExplorativeSimulation(omni_simulation, goal, verbose=verbose,
                                     require_energy=require_energy, ti=ti, bidi=bidi, collect_crystals=dump_crystals)

    if verbose:
        wipe_screen()
    print(explorer)

    if dump_crystals:
        for i in range(explorer.lower_bound, explorer.upper_bound + 1):
            d = explorer.data_index(i)
            comparison = None
            if i < len(explorer.TEST_ENERGIES):
                comparison = explorer.comparison(i)
            file: Path = dump_crystals / crystal_file_name(dimension, i, require_energy, bidi, ti, initial, comparison)
            if file.exists():
                log.error(f"File {file} already exists")
                continue
            string: str = "\n".join("["
                                    + ", ".join(map(str, c.atoms()))
                                    + "]"
                                    for c in explorer.crystals[d])
            log.info(f"Writing {len(string)} bytes to {file.absolute()}")
            file.write_text(string)
            assert os.path.getsize(file) != 0, f"File {file} was not written"
