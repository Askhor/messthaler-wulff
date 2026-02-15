import logging
import os
from pathlib import Path

import colorama.ansi
from colorama import Cursor

from messthaler_wulff._additive_simulation import OmniSimulation, SimpleNeighborhood
from messthaler_wulff.decorators import wipe_screen
from messthaler_wulff.explorative_simulation import ExplorativeSimulation

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


def crystal_file_name(dimension, count, require_energy, bidi, ti, initial):
    mode = ""
    if bidi:
        mode += "b"
    if ti:
        mode += "t"
    if require_energy is not None:
        mode += str(require_energy)
    if initial is not None:
        mode += f"i{len(initial)}"
    return f"Crystals in {dimension}d with {count} atoms (mode: {mode}).txt"


def run_mode(goal, lattice, dimension: int, dump_crystals=None, verbose=False, initial=(),
             require_energy=None, ti=True, bidi=True):
    omni_simulation = OmniSimulation(SimpleNeighborhood(lattice), None, tuple([0] * (dimension + 1)))
    for atom in initial:
        omni_simulation.force_set_atom(atom, OmniSimulation.FORWARDS)
    explorer = ExplorativeSimulation(omni_simulation, goal, verbosity=2 if verbose else 0,
                                     require_energy=require_energy, ti=ti, bidi=bidi, collect_crystals=dump_crystals)

    if verbose:
        wipe_screen()
    print(explorer)

    if dump_crystals is not None:
        if dump_crystals == "-":
            string: str = "\n".join("["
                                    + ", ".join(map(str, c.atoms()))
                                    + "]"
                                    for c in explorer.crystals[explorer.data_index(goal)])
            print()
            print(string)
        else:
            dump_crystals = Path(dump_crystals)
            for i in range(explorer.lower_bound, explorer.upper_bound + 1):
                d = explorer.data_index(i)
                file: Path = dump_crystals / crystal_file_name(dimension, i, require_energy, bidi, ti, initial)
                if file.exists():
                    log.error(f"File {file} already exists")
                    continue
                string = "\n".join("["
                                        + ", ".join(map(str, c.atoms()))
                                        + "]"
                                        for c in explorer.crystals[d])
                log.info(f"Writing {len(string)} bytes to {file.absolute()}")
                assert file.write_text(string) != 0, f"File {file} was not written to"
                assert os.path.getsize(file) != 0, f"File {file} was not written to"
