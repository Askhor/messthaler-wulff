from typing import Any

from networkx import Graph

from messthaler_wulff.sim.qbv_simulation import QBVSimulation


def _gen_impl(sim: QBVSimulation, nodes: list[Any], index: int):
    if index == len(nodes):
        yield sim
        return

    node = nodes[index]

    yield from _gen_impl(sim, nodes, index + 1)
    sim.toggle(node)
    yield from _gen_impl(sim, nodes, index + 1)
    sim.toggle(node)


def generate_states(graph: Graph):
    sim = QBVSimulation(graph)
    nodes = list(graph.nodes)

    yield from _gen_impl(sim, nodes, 0)
