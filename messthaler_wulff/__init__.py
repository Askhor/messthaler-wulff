import argparse
import hashlib
import logging
import math
import os
import sys
from abc import abstractmethod, ABC
from argparse import ArgumentParser

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


def parse_hash_function(algo):
    if algo not in hashlib.algorithms_available:
        log.error(f"Unknown hash algorithm {algo}")
        log.error(f"The following hash algorithms are available: {", ".join(hashlib.algorithms_available)}")
        raise ValueError()

    return lambda: hashlib.new(algo)


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


class Mode(ABC):
    modes = []

    @classmethod
    @abstractmethod
    def create_parser(cls, obj) -> ArgumentParser:
        parser = obj.add_parser(cls.name, description=cls.description, help=cls.description)
        parser.set_defaults(mode=cls)
        return parser

    @classmethod
    @abstractmethod
    def call(cls, args):
        pass


@Mode.modes.append
class View(Mode):
    name = "view"
    description = "Use Matplotlib to visualise a crystal in 3d"

    @classmethod
    def create_parser(cls, obj):
        parser = super().create_parser(obj)
        parser.add_argument("-o", "--orthogonal", action="store_true")
        parser.add_argument("-a", "--axis", action="store_true")
        parser.add_argument("-p", "--points", action="store_true")
        parser.add_argument("-l", "--lines", type=float, default=None)
        parser.add_argument("-c", "--convex-hull", action="store_true")
        return parser

    @classmethod
    def call(cls, args):
        if not (args.axis or args.points or args.lines):
            log.error("At least one of the following must be present for view: -p, -l or -c")
            sys.exit(1)

        from .mode_view import run_mode
        run_mode(use_orthogonal_projection=args.orthogonal,
                 show_axes=args.axis,
                 show_points=args.points,
                 line_length=args.lines,
                 show_convex_hull=args.convex_hull,
                 initial=parse_initial_crystal(args.initial_crystal, args.dimension),
                 lattice=args.lattice)


@Mode.modes.append
class Interactive(Mode):
    name = "interactive"
    description = "Explore a 2d slice of a crystal using commands"

    @classmethod
    def create_parser(cls, obj) -> ArgumentParser:
        parser = super().create_parser(obj)
        return parser

    @classmethod
    def call(cls, args):
        from .mode_interactive import run_mode
        run_mode(goal=int(args.goal), dimension=args.dimension,
                 lattice=args.lattice, windows_mode=args.windows,
                 initial=parse_initial_crystal(args.initial_crystal, args.dimension))


@Mode.modes.append
class Simulate(Mode):
    name = "simulate"
    description = "Simulate massive crystals in 3d (On Linux may require environment variable XDG_SESSION_TYPE=x11)"

    @classmethod
    def create_parser(cls, obj) -> ArgumentParser:
        parser = super().create_parser(obj)
        return parser

    @classmethod
    def call(cls, args):
        os.environ["XDG_SESSION_TYPE"] = "x11"
        from .mode_simulate import run_mode
        run_mode(goal=args.goal, lattice=args.lattice)


@Mode.modes.append
class Explore(Mode):
    name = "explore"
    description = "Explore the number of crystals and optimal energies"

    @classmethod
    def create_parser(cls, obj) -> ArgumentParser:
        parser = super().create_parser(obj)
        parser.add_argument("--dump-crystals", action="store_true")
        parser.add_argument("--hash-function", default="sha256", type=parse_hash_function,
                            help="(default: %(default)s)")
        return parser

    @classmethod
    def call(cls, args):
        from .mode_explore import run_mode
        run_mode(goal=args.goal, lattice=args.lattice, dimension=args.dimension,
                 dump_crystals=args.dump_crystals, hash_function=args.hash_function)


def main():
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME,
                                     description="Wudduwudduwudduwudduwudduwudduwudduwuddu")

    parser.add_argument('-v', '--verbose', action='store_true', help="Show more output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {program_version}")

    parser.add_argument("--goal", help="The number of atoms to add initially or to go to (default: %(default)s)",
                        type=int,
                        default=20)

    lattice_options = parser.add_argument_group("Lattice Options")
    lattice_options.add_argument("--lattice", default="fcc", type=parse_lattice, help="(default: %(default)s)")
    lattice_options.add_argument("--dimension", default="3", type=int, help="(default: %(default)s)")
    lattice_options.add_argument("--initial-crystal", default=None)

    parser.add_argument("-w", "--windows", action="store_true")

    subparsers = parser.add_subparsers(title="Modes", description="Possible modes of operation", required=True)
    for mode in Mode.modes:
        mode.create_parser(subparsers)

    args = parser.parse_args()

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log.debug("Starting program...")

    args.mode.call(args)
