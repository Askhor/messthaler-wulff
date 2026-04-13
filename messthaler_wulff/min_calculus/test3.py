import abc
import functools
import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Iterator, Self, Any, Iterable

import matplotlib.pyplot as plt
import networkx as nx
import tqdm


@functools.total_ordering
@dataclass(frozen=True)
class Candidate:
    values: int  # Bitmask representing the nodes included
    dependencies: int  # Bitmask for dependencies
    energy: int

    def __lt__(self, other: Self):
        return self.energy < other.energy

    def __repr__(self):
        return f"C{{{self.bitmask_to_list(self.values)}|{self.bitmask_to_list(self.dependencies)}|{self.energy}}}"

    def __format__(self, format_spec):
        return format(str(self), format_spec)

    @staticmethod
    def bitmask_to_list(mask: int) -> list[int]:
        return [i for i in range(mask.bit_length()) if (mask & (1 << i)) != 0]


type CandidateCollection = dict[Any, Candidate]


class Solver(abc.ABC):
    def __init__(self, graph: nx.Graph, nodes: list[Any], node_weight, edge_weight: int, upper_bound: int = -1):
        self.graph: nx.Graph = graph
        self.nodes: list[Any] = nodes
        self.indices = {n: i for i, n in enumerate(nodes)}
        self.node_weight = node_weight
        self.edge_weight: int = edge_weight
        self.candidates: CandidateCollection = {}
        self.add_candidate(Candidate(0, 0, 0))
        if upper_bound == -1:
            upper_bound = len(nodes)
        self.upper_bound = upper_bound
        self.candidate_counts = [1]

    @abc.abstractmethod
    def classify_candidate(self, candy: Candidate) -> Any:
        ...

    def solve(self) -> list[int]:
        energies = [math.inf] * (self.upper_bound + 1)

        pbar = tqdm.tqdm(range(len(self.nodes)), position=0)
        for i in pbar:
            start_time = time.time()
            old_candidates = self.candidates
            self.candidates = {}
            self.step(old_candidates, i)
            self.candidate_counts.append(len(self.candidates))
            end_time = time.time()
            """5.8e-06s"""

            time_per_candy = (end_time - start_time) / len(self.candidates)

            pbar.set_description(
                f"Nr. candidates: {len(self.candidates)} ({len(self.candidates) / 2 ** math.sqrt(len(self.nodes)):6.2%}), "
                f"{time_per_candy:.2}s")

        for candy in self.candidates.values():
            size = self.bit_count(candy.values)
            energies[size] = min(energies[size], candy.energy)

        return energies

    def add_candidate(self, candy: Candidate):
        key = self.classify_candidate(candy)
        if key in self.candidates and self.candidates[key].energy <= candy.energy:
            return
        self.candidates[key] = candy

    def step(self, old_candidates: CandidateCollection, node_index: int):
        for candy in old_candidates.values():
            self.add_candidate(self.without_atom(candy, node_index))

            if self.bit_count(candy.values) >= self.upper_bound:
                continue
            self.add_candidate(self.with_atom(candy, node_index))

    def neighbors(self, node_index: int) -> Iterable[int]:
        for n in self.graph.neighbors(self.nodes[node_index]):
            index = self.indices[n]
            yield index

    def without_atom(self, candy: Candidate, node_index: int) -> Candidate:
        return Candidate(candy.values, candy.dependencies & ~(1 << node_index), candy.energy)

    def with_atom(self, candy: Candidate, node_index: int) -> Candidate:
        node = self.nodes[node_index]
        energy_delta = self.node_weight(node)
        for n in self.neighbors(node_index):
            if (candy.values & (1 << n)) != 0:
                energy_delta += 2 * self.edge_weight

        new_dependencies = 0
        for n in self.neighbors(node_index):
            if n > node_index:
                new_dependencies |= (1 << n)

        new_values = candy.values | (1 << node_index)
        new_dependencies |= (candy.dependencies & ~(1 << node_index))  # Remove the current node from dependencies

        return Candidate(new_values, new_dependencies, candy.energy + energy_delta)

    @staticmethod
    def bit_count(x: int) -> int:
        return x.bit_count()


class BFSolver(Solver):
    def classify_candidate(self, candy: Candidate) -> Any:
        return candy


class SmartSolver(Solver):
    def classify_candidate(self, candy: Candidate) -> Any:
        return self.bit_count(candy.values), candy.dependencies


class ID:
    def __getitem__(self, x):
        return x


def bfs(graph: nx.Graph, root) -> Iterator:
    queue = deque([root])
    visited = set()

    while len(queue) > 0:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)

        yield node

        for n in graph.neighbors(node):
            queue.append(n)


def main():
    atoms = 30
    graph: nx.Graph = nx.grid_2d_graph(atoms, atoms, False)
    assert not (set(bfs(graph, (0, 0))) ^ set(graph.nodes))

    node_weight = lambda *args: 4
    edge_weight = -1

    nodes = list(bfs(graph, (0, 0)))
    solver = SmartSolver(graph, nodes, node_weight, edge_weight, atoms)
    solutions = solver.solve()

    for i, candy in enumerate(solutions):
        print(f"{i:2}: {candy:>80}")

    plt.plot(range(len(solver.candidate_counts)), solver.candidate_counts)
    plt.show()


if __name__ == "__main__":
    main()
