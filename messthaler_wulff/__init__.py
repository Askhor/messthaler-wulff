# PYTHON_ARGCOMPLETE_OK


from argparse import ArgumentParser

import argcomplete
import mydefaults

from . import mylog
from .modes import mode_energies, mode_crystals, mode_stats, mode_plot_crystal
from .version import program_version

mylog.init()


# def parse_initial_crystal(initial_crystal, dimension):
#     if initial_crystal is None:
#         return []
#
#     if initial_crystal == "-":
#         initial_crystal = input("Input initial crystal: ")
#
#     value = parse_crystal(initial_crystal)
#     log.info(f"Initial crystal has been set to {value}")
#
#     for i in range(len(value)):
#         l = len(value[i])
#         if l != dimension + 1:
#             value[i] = tuple([0] * (dimension + 1 - l) + list(value[i]))
#
#     log.info(f"Value has been normalised to {value}")
#     input("Press enter to continue...")
#
#     return value


# @mydefaults.sub_command
# def view(parser: ArgumentParser) -> mydefaults.MAGIC:
#     """Use Matplotlib to visualize a crystal in 3d"""
#     parser.add_argument("-o", "--orthogonal", action="store_true")
#     parser.add_argument("-a", "--axis", action="store_true")
#     parser.add_argument("-p", "--points", action="store_true")
#     parser.add_argument("-l", "--lines", type=float, default=None)
#     parser.add_argument("-c", "--convex-hull", action="store_true")
#
#     args = yield
#
#     if not (args.axis or args.points or args.lines):
#         log.error("At least one of the following must be present for view: -p, -l or -c")
#         sys.exit(1)
#
#     from messthaler_wulff.modes.mode_view import run_mode
#     run_mode(use_orthogonal_projection=args.orthogonal,
#              show_axes=args.axis,
#              show_points=args.points,
#              line_length=args.lines,
#              show_convex_hull=args.convex_hull,
#              initial=parse_initial_crystal(args.initial_crystal, args.dimension),
#              lattice=args.lattice)
#
#
# @mydefaults.sub_command
# def interactive(parser: ArgumentParser) -> mydefaults.MAGIC:
#     """Explore a 2d slice of a crystal using commands"""
#
#     args = yield
#
#     from messthaler_wulff.modes.mode_interactive import run_mode
#     run_mode(goal=int(args.goal), dimension=args.dimension,
#              lattice=args.lattice, windows_mode=False,
#              initial=parse_initial_crystal(args.initial_crystal, args.dimension))
#
#
# @mydefaults.sub_command
# def simulate(parser: ArgumentParser) -> mydefaults.MAGIC:
#     """Simulate massive crystals in 3d (On Linux may require environment variable XDG_SESSION_TYPE=x11)"""
#     args = yield
#     os.environ["XDG_SESSION_TYPE"] = "x11"
#     from messthaler_wulff.modes.mode_simulate import run_mode
#     run_mode(goal=args.goal, lattice=args.lattice)
#
#
# @mydefaults.sub_command
# def explore(parser: ArgumentParser) -> mydefaults.MAGIC:
#     """Explore the number of crystals and optimal energies"""
#
#     parser.add_argument("-d", "--dump-crystals", default=None)
#     parser.add_argument("-r", "--require-energy", type=int, default=None)
#     parser.add_argument("--no-translations", action="store_true")
#     parser.add_argument("--no-bidi", action="store_true")
#
#     args = yield
#
#     from messthaler_wulff.modes.mode_explore import run_mode
#     run_mode(goal=args.goal, lattice=args.lattice,
#              initial=parse_initial_crystal(args.initial_crystal, args.dimension),
#              dimension=args.dimension, verbose=args.verbose, dump_crystals=args.dump_crystals,
#              require_energy=args.require_energy, ti=not args.no_translations, bidi=not args.no_bidi)


@mydefaults.command(version=program_version)
def messthaler_wulff(parser: ArgumentParser):
    """Blazingly fast code for finding all crystals
    (subsets of a graph) that can be constructed
    using only transformations that locally minimize
    surface energy."""

    # parser.add_argument("--goal", help="The number of atoms to add initially or to go to (default: %(default)s)",
    #                     type=int,
    #                     default=20)
    #
    # lattice_options = parser.add_argument_group("Lattice Options")
    # lattice_options.add_argument("--lattice", default="fcc", type=parse_lattice, help="(default: %(default)s)")
    # lattice_options.add_argument("--dimension", default="3", type=int, help="(default: %(default)s)")
    # lattice_options.add_argument("--initial-crystal", default=None)

    subparsers = parser.add_subparsers(title="Modes", description="Possible modes of operation", required=True)
    mydefaults.add_sub_commands(subparsers)

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    mylog.set_level(args.quiet - args.verbose)
    mylog.log.debug("Starting program...")

    mydefaults.run_sub_command(args)
