import argparse
import hashlib
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
    parser.add_argument("--version", action="version", version=f"%(prog)s {program_version}")
    parser.add_argument("MODE",
                        help=f"What subprogram to execute; Can be {MODE_STRING}")

    parser.add_argument("--goal", help="The number of atoms to add initially (default: %(default)s)", type=int,
                        default="100")
    parser.add_argument("--dump-crystals", action="store_true")

    parser.add_argument("-o", "--view-options", default="acp",
                        help=("A sequence of letters the presence of which indicates certain suboptions: "
                              "a - Show axis, "
                              "o - Use orthogonal projection, "
                              "p - Show points, "
                              "l - Insert lines between points, "
                              "c - Show convex hull of points"))

    lattice_options = parser.add_argument_group("Lattice Options")
    lattice_options.add_argument("--lattice", default="fcc", help="(default: %(default)s)")
    lattice_options.add_argument("--dimension", default="3", type=int, help="(default: %(default)s)")
    lattice_options.add_argument("--initial-crystal", default=None)

    internal_options = parser.add_argument_group("Internal Options")
    internal_options.add_argument("--hash-function", default="sha256", help="(default: %(default)s)")
    internal_options.add_argument("-w", "--windows", action="store_true")

    args = parser.parse_args()

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log.debug("Starting program...")

    if args.hash_function not in hashlib.algorithms_available:
        log.error(f"Unknown hash algorithm {args.hash_function}")
        log.error(f"The following hash algorithms are available: {", ".join(hashlib.algorithms_available)}")

    hash_function = lambda: hashlib.new(args.hash_function)

    dimension = int(args.dimension)

    match args.MODE.lower():
        case 'view':
            from . import mode_view
            mode_view.run_mode(use_orthogonal_projections="o" in args.view_options,
                               show_axes="a" in args.view_options,
                               show_points="p" in args.view_options,
                               show_lines="l" in args.view_options,
                               show_convex_hull="c" in args.view_options,
                               initial=parse_initial_crystal(args.initial_crystal, dimension),
                               lattice=parse_lattice(args.lattice))
        case 'simulate':
            from . import mode_simulate
            mode_simulate.run_mode(goal=int(args.goal), lattice=parse_lattice(args.lattice))
        case 'interactive':
            from . import mode_interactive
            mode_interactive.run_mode(goal=int(args.goal), dimension=dimension,
                                      lattice=parse_lattice(args.lattice), windows_mode=args.windows,
                                      initial=parse_initial_crystal(args.initial_crystal, dimension))
        case 'explore':
            from . import mode_explore
            mode_explore.run_mode(goal=int(args.goal), lattice=parse_lattice(args.lattice),
                                  dimension=int(args.dimension), dump_crystals=args.dump_crystals,
                                  hash_function=hash_function)
        case 'minimisers':
            from . import mode_minimisers
            mode_minimisers.run_mode(goal=int(args.goal), lattice=parse_lattice(args.lattice),
                                     dimension=int(args.dimension), dump_crystals=args.dump_crystals,
                                     hash_function=hash_function)
        case _:
            log.error(f"Unknown mode {args.MODE}. Must be one of {MODE_STRING}")
