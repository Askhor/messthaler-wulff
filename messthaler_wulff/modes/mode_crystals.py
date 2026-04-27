from argparse import ArgumentParser

import mydefaults

from messthaler_wulff.parsing import crystals as crystals_parser, graphs
from messthaler_wulff.sim.anneal import Anneal


@mydefaults.sub_command
def crystals(parser: ArgumentParser) -> mydefaults.MAGIC:
    graphs.add_arguments(parser)
    parser.add_argument("atom_count", type=int)
    parser.add_argument("energy", type=int)

    parser.add_argument("-m", "--maximum", type=int, default=10)

    args = yield

    atom_count = args.atom_count
    energy = args.energy

    graph = graphs.graph_from_args(args)
    anneal = Anneal(graph, 2 * atom_count + 5)

    crystal_count = 0

    for state in anneal.generate_states():
        if state.size == atom_count and state.energy == energy:
            print(crystals_parser.to_json(state.nodes))
            crystal_count += 1
            if crystal_count > args.maximum:
                break
