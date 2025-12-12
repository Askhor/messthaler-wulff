import argparse
import logging
import math

import numpy as np

from .data import fcc_transform
from .terminal_formatting import parse_color
from .version import program_version

log = logging.getLogger("messthaler_wulff")
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.DEBUG)
console.setFormatter(
    logging.Formatter(parse_color("{asctime} [ℂ3.{levelname:>5}ℂ.] ℂ4.{name}ℂ.: {message}"),
                      style="{", datefmt="%W %a %I:%M"))

PROGRAM_NAME = "messthaler-wulff"
DEFAULT_DATE_FORMAT = "%y/%b/%NAME"


def command_entry_point():
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Program was interrupted by user")


def parse_lattice(lattice):
    match lattice.lower():
        case "fcc":
            return fcc_transform()

    log.info(f"Unknown lattice name {lattice}, interpreting lattice as python code")

    transform = np.array(eval(lattice, {"sqrt": math.sqrt}))

    log.info(f"Using result as lattice transform:\n{transform}")

    input("Press enter to continue...")
    return transform


def parse_initial_crystal(initial_crystal, dimension):
    if initial_crystal is None:
        return []

    value = eval(initial_crystal)
    log.info(f"Initial crystal has been set to {value}")

    for i in range(len(value)):
        l = len(value[i])
        if l != dimension + 1:
            value[i] = tuple([0] * (dimension + 1 - l) + list(value[i]))

    log.info(f"Value has been normalised to {value}")
    input("Press enter to continue...")

    return value


def main():
    MODES = "view", "simulate", "interactive", "explore", "minimisers"
    MODE_STRING = " or ".join("'" + m + "'" for m in MODES)

    parser = argparse.ArgumentParser(prog=PROGRAM_NAME,
                                     description="Wudduwudduwudduwudduwudduwudduwudduwuddu",
                                     allow_abbrev=True, add_help=True, exit_on_error=True)

    parser.add_argument('-v', '--verbose', action='store_true', help="Show more output")
    parser.add_argument("--version", action="store_true", help="Show the current version of the program")
    parser.add_argument("MODE",
                        help=f"What subprogram to execute; Can be {MODE_STRING}")
    parser.add_argument("--goal", help="The number of atoms to add initially", default="100")
    parser.add_argument("--dimension", default="3")
    parser.add_argument("--lattice", default="fcc")
    parser.add_argument("--axis", action="store_true")
    parser.add_argument("--orthogonal", action="store_true")
    parser.add_argument("--dump-crystals", action="store_true")
    parser.add_argument("-w", "--windows", action="store_true")
    parser.add_argument("--initial-crystal", default=None)

    args = parser.parse_args()

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log.debug("Starting program...")

    if args.version:
        log.info(f"{PROGRAM_NAME} version {program_version}")
        return

    match args.MODE.lower():
        case 'view':
            from . import mode_view
            mode_view.run_mode(use_orthogonal_projections=args.orthogonal, show_axes=args.axis)
        case 'simulate':
            from . import mode_simulate
            mode_simulate.run_mode(goal=int(args.goal), lattice=parse_lattice(args.lattice))
        case 'interactive':
            from . import mode_interactive
            dimension = int(args.dimension)
            mode_interactive.run_mode(goal=int(args.goal), dimension=dimension,
                                      lattice=parse_lattice(args.lattice), windows_mode=args.windows,
                                      initial=parse_initial_crystal(args.initial_crystal, dimension))
        case 'explore':
            from . import mode_explore
            mode_explore.run_mode(goal=int(args.goal), lattice=parse_lattice(args.lattice),
                                  dimension=int(args.dimension), dump_crystals=args.dump_crystals)
        case 'minimisers':
            from . import mode_minimisers
            mode_minimisers.run_mode(goal=int(args.goal), lattice=parse_lattice(args.lattice),
                                     dimension=int(args.dimension), dump_crystals=args.dump_crystals)
        case _:
            log.error(f"Unknown mode {args.MODE}. Must be one of {MODE_STRING}")
