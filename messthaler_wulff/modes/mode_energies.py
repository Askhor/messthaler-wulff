import math
from argparse import ArgumentParser
from enum import Enum

import mydefaults
from prettytable import PrettyTable

from messthaler_wulff.math.bravais import CommonBravais
from messthaler_wulff.sim import energies as nrg
from messthaler_wulff.sim.anneal import Anneal


class Strategy(Enum):
    BRUTE_FORCE = "bruteforce"
    ANNEAL = "anneal"

    def __str__(self):
        return self.value


@mydefaults.sub_command
def energies(parser: ArgumentParser) -> mydefaults.MAGIC:
    parser.add_argument("graph")
    parser.add_argument("upper_bound", type=int)

    parser.add_argument("-s", "--strategy", choices=Strategy)
    parser.add_argument("--timeout", type=float, default=4)
    parser.add_argument("--no-improve2reset", action="store_true")

    args = yield

    graph = CommonBravais.fcc.value.graph(args.graph_size)
    upper_bound = args.upper_bound if args.upper_bound is not None else len(graph)
    anneal = Anneal(graph, upper_bound)
    res = nrg.find(anneal.generate_states(), args.timeout, not args.no_improve2reset)

    table = PrettyTable(["Atoms", "Minimal Energy"], align='r')
    table.custom_format = lambda f, v: f"{v:,}"

    for i in range(upper_bound):
        table.add_row([i, res[i] if i in res else math.nan])

    print(table)
