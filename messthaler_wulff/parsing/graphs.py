from argparse import ArgumentParser
from pathlib import Path
from typing import Literal, Union, Optional

import networkx as nx
import numpy as np
from networkx import Graph
from pydantic import BaseModel, RootModel, Field

from messthaler_wulff.math import bravais as bravais_mod
from messthaler_wulff.math.bravais import Bravais, CommonBravais
from messthaler_wulff.parsing.common import VectorModel, NodeModel, list2vec


class BravaisModel(BaseModel):
    type: Literal["bravais"]
    primitives: list[VectorModel]
    transform: Optional[list[list[float]]] = None

    def get_bravais(self):
        if self.transform is None:
            transform = self.transform
        else:
            transform = np.array(self.transform)

        return Bravais(list(map(list2vec, self.primitives)), transform)

    def plot(self, args: list[str]):
        bravais = self.get_bravais()
        graph = self.get_graph(args)

        bravais_mod.plot_bravais(bravais, graph)

    def get_graph(self, args: list[str]):
        bravais = self.get_bravais()

        return _get_graph_bravais(bravais, args)


class FiniteGraphModel(BaseModel):
    type: Literal["finite"]
    nodes: list[NodeModel]
    edges: list[tuple[NodeModel, NodeModel]]

    def get_graph(self, args: list[str]):
        assert len(args) == 0  # TODO
        graph = Graph()
        graph.add_nodes_from(list(map(list2vec, self.nodes)))
        graph.add_edges_from([(list2vec(a), list2vec(b), {"weight": -1}) for a, b in self.edges])
        for n in graph:
            graph.nodes[n]["weight"] = graph.degree(n)
        return graph

    def plot(self, args: list[str]):
        graph = self.get_graph(args)
        nx.draw(graph)


class GraphModel(RootModel):
    root: Union[BravaisModel, FiniteGraphModel] = Field(discriminator="type")


def _get_graph_bravais(b: Bravais, args: list[str]):
    assert len(args) == 1  # TODO
    return b.graph(int(args[0]))


def get_graph(path: Path, args: list[str]):
    for bravais in CommonBravais:
        if bravais.name == str(path):
            return _get_graph_bravais(bravais.value, args)

    if path == Path("-"):
        string = input("Enter graph json here: ")
    else:
        assert path.exists()  # TODO
        string = path.read_text()

    model = GraphModel.model_validate_json(string)
    return model.root.get_graph(args)


def add_arguments(parser: ArgumentParser):
    parser.add_argument("graph", type=Path)
    parser.add_argument("-p", "--graph-parameter", type=int, default=None)


def graph_from_args(args):
    graph_parameters = [] if args.graph_parameter is None else [args.graph_parameter]
    graph = get_graph(args.graph, graph_parameters)
    return graph
