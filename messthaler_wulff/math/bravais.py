import math
from enum import Enum
from typing import Iterator

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from messthaler_wulff import mylog
from messthaler_wulff.math.vector import vec


class Bravais:
    """A class representing Bravais lattices for crystallography."""

    def __init__(self, primitives: list[vec], transform: np.ndarray = None) -> None:
        """
                Initialize the Bravais lattice with given primitive vectors and an optional transformation matrix.

                Args:
                    primitives (list[vec]): A list of primitive vectors constituting the lattice.
                    transform (np.ndarray, optional): A transformation matrix. If None, an identity matrix is used.

                Raises:
                    ValueError: If the primitives are invalid.
                """
        self.check_primitives(primitives)
        self.dimension = len(primitives[0])
        assert all(len(v) == self.dimension for v in primitives)
        self._primitives = primitives
        self.degree = 2 * len(self._primitives)
        self.zero = vec.zero(self.dimension)

        if transform is None:
            self.transform = np.identity(self.dimension)
        else:
            assert transform.shape == (self.dimension, self.dimension)
            self.transform = transform

    @staticmethod
    def check_primitives(primitives: list[vec]):
        """
                Check if the provided primitive vectors are valid.

                Args:
                    primitives (list[vec]): A list of primitive vectors to check.

                Raises:
                    ValueError: If the primitives contain inverses of any vectors or are not unique.
                """
        try:
            ps = set(primitives)
        except TypeError:
            raise ValueError(f"Could transform primitives into set: {primitives}")
        for p in primitives:
            if -p in ps:
                raise ValueError("Primitives contain inverses of some vector(s)")

    def primitive(self, index: int) -> vec:
        """
                Retrieve a primitive vector by its index, accounting for inverse vectors.

                Args:
                    index (int): The index of the desired primitive vector.

                Returns:
                    vec: The corresponding primitive vector, potentially negated.
                """
        k = len(self._primitives)
        if index >= k:
            index -= k
            return -self._primitives[index]

        return self._primitives[index]

    def neighbor(self, node: vec, index: int) -> vec:
        """
                Calculate the neighboring vector by adding a primitive vector to a given node.

                Args:
                    node (vec): The vector representing the current node.
                    index (int): The index of the primitive vector to add.

                Returns:
                    vec: The resulting neighboring vector.
                """
        assert len(node) == self.dimension
        return node + self.primitive(index)

    def bfs(self, radius: int) -> Iterator[vec]:
        """
                Perform a breadth-first search (BFS) up to a specified radius.

                Args:
                    radius (int): The search radius.

                Yields:
                    Iterator[vec]: The vector nodes encountered during the BFS.
                """
        current_nodes = {self.zero}
        visited = set()

        for i in range(radius + 1):
            yield from current_nodes

            next_nodes = set()
            visited |= current_nodes

            for node in current_nodes:
                for j in range(self.degree):
                    n = self.neighbor(node, j)
                    if n not in visited:
                        next_nodes.add(n)

            current_nodes = next_nodes

    def graph(self, radius: int) -> nx.Graph:
        """
                Generate a graph representation of the Bravais lattice within a specified radius.

                Args:
                    radius (int): The radius for BFS in the lattice.

                Returns:
                    nx.Graph: A NetworkX graph representing the lattice structure.
                """
        g = nx.Graph()

        nodes = set(mylog.tqdm(self.bfs(radius), desc="Generating graph"))
        g.add_nodes_from((n, {"weight": self.degree}) for n in nodes)

        for node in mylog.tqdm(nodes, desc="Adding edges"):
            for i in range(self.degree):
                n = self.neighbor(node, i)
                if n in nodes:
                    g.add_edge(node, n, weight=-1)

        return g

    def __str__(self):
        return str(self._primitives)


def plot_bravais(bravais: Bravais,
                 graph: nx.Graph,
                 ax=None,
                 node_color="blue",
                 edge_color="black",
                 node_alpha=0.8,
                 edge_alpha=1.0):
    """
        Plot the Bravais lattice graph using Matplotlib.

        Args:
            bravais (Bravais): The Bravais object representing the lattice.
            graph (nx.Graph): The graph representation of the lattice.
            ax (matplotlib.axes.Axes, optional): The axes to plot on. If None, a new one will be created.
            node_color (str, optional): Color of the nodes. Default is "blue".
            edge_color (str, optional): Color of the edges. Default is "black".
            node_alpha (float, optional): Opacity of the nodes. Default is 0.8.
            edge_alpha (float, optional): Opacity of the edges. Default is 1.0.

        Returns:
            matplotlib.axes.Axes: The axes with the plotted Bravais lattice.
        """
    assert bravais.dimension in [2, 3], bravais.dimension

    if ax is None:
        ax = plt.figure().add_subplot(projection='3d' if bravais.dimension == 3 else None)
        ax.set_aspect('equal')

    pos = lambda n: bravais.transform @ n

    nodes = np.array([pos(v) for v in graph])
    edges = np.array([(pos(u), pos(v)) for u, v in graph.edges()])

    ax.scatter(*nodes.T, s=100, color=node_color, alpha=node_alpha)
    for vizedge in edges:
        ax.plot(*vizedge.T, color=edge_color, alpha=edge_alpha)

    return ax


class CommonBravais(Enum):
    """Enum representation of common Bravais lattices."""
    square = Bravais([
        vec.new(1, 0),
        vec.new(0, 1)])

    cubic = Bravais([
        vec.new(1, 0, 0),
        vec.new(0, 1, 0),
        vec.new(0, 0, 1)])

    triangular = Bravais([
        vec.new(1, 0),
        vec.new(1, 1),
        vec.new(0, 1)],
        np.array([[1, -math.cos(math.pi / 3)],
                  [0, math.sin(math.pi / 3)], ]))

    fcc = Bravais([
        vec.new(1, 0, 0),
        vec.new(0, 1, 0),
        vec.new(0, 0, 1),
        vec.new(-1, 0, 1),
        vec.new(1, -1, 0),
        vec.new(0, 1, -1)],
        1 / math.sqrt(2) * np.array([[1, 1, 0],
                                     [1, 0, 1],
                                     [0, 1, 1]]))
