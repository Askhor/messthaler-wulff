import shutil
import textwrap
from enum import Enum
from functools import partial
from typing import Iterable, Sequence, Optional

from colorama import Fore, Back

from messthaler_wulff.common_lattices import CommonLattice
from messthaler_wulff.decorators import compose
from messthaler_wulff.graph import Graph, Lattice
from messthaler_wulff.priority_stack import PriorityStack


class Mode(Enum):
    BACKWARDS = 0, -1
    FORWARDS = 1, 1

    def __init__(self, index: int, sign: int):
        super().__init__()
        self.index = index
        self.sign = sign


class AdditiveSimulation:
    """A blazingly fast simulation of crystals (subsets of a lattice/graph)
    and transformations (addition/removal) which locally minimize surface energy"""

    def __init__(self, graph: Graph) -> None:
        self.energy = 0
        self.size = 0
        self.graph = graph

        self.boundaries = [PriorityStack(graph.max_degree + 1),
                           PriorityStack(graph.max_degree + 1)]
        self.boundary(Mode.FORWARDS).set_priority(
            Graph.ZERO,
            self.calculate_loneliness(Graph.ZERO, Mode.FORWARDS))

        assert (self.boundary(Mode.FORWARDS).get_priority(Graph.ZERO)
                == self.calculate_loneliness(Graph.ZERO, Mode.FORWARDS))

    def boundary(self, mode: Mode) -> PriorityStack:
        """The priority stack containing values and energies
        that are next in line to be added when going in the
        'mode' direction"""
        return self.boundaries[mode.index]

    def reverse_boundary(self, mode: Mode) -> PriorityStack:
        """The priority stack containing values and energies
        of nodes that are already in the crystal when going
        in the 'mode' direction"""
        return self.boundaries[1 - mode.index]

    def calculate_loneliness(self, node: int, mode: Mode) -> int:
        energy = self.graph.degree(node)
        reverse_boundary = self.reverse_boundary(mode)

        for neighbor in self.graph.neighbors(node):
            if neighbor in reverse_boundary:
                energy -= 1

        return energy

    def move_to_boundary(self, node: int, mode: Mode) -> None:
        self.size += mode.sign
        assert self.size >= 0

        mode_boundary = self.boundary(mode)
        reverse_boundary = self.reverse_boundary(mode)

        assert node in mode_boundary
        assert node not in reverse_boundary

        old_loneliness = mode_boundary.get_priority(node)
        neighbors = self.graph.neighbors(node)
        degree = len(neighbors)
        self.energy += 2 * old_loneliness - degree

        mode_boundary.unset_priority(node)
        reverse_boundary.set_priority(node, degree - old_loneliness)

        for n in neighbors:
            if n in mode_boundary:
                mode_boundary.increment(n, -1, self.graph.degree(n))
            elif n in reverse_boundary:
                reverse_boundary.increment(n, 1, self.graph.degree(n))
            else:
                mode_boundary.set_priority(n, self.graph.degree(n) - 1)

    def next(self, mode: Mode) -> Sequence[int]:
        return self.boundary(mode).minimums()

    @partial(compose, list)
    def invariant_failures(self) -> Iterable[str]:
        """Returns a list of strings of which invariants do
        not hold on this instance"""

        if self.energy < 0:
            yield f"Negative energy: {self.energy}"

        for mode in [Mode.BACKWARDS, Mode.FORWARDS]:
            boundary = self.boundary(mode)
            reverse_boundary = self.reverse_boundary(mode)

            for node in boundary:
                if node in reverse_boundary:
                    yield f"A node cannot be in multiple boundaries at once"
                    continue

                loneliness = self.calculate_loneliness(node, mode)
                if loneliness >= self.graph.degree(node) and self.size > 0:
                    yield f"Failed {loneliness} < {self.graph.degree(node)} (node: {node})"
                    continue

                if boundary.get_priority(node) != loneliness:
                    yield f"Stored loneliness {boundary.get_priority(node)} does not match calculated {loneliness}"
                    continue

    def test_invariants(self) -> None:
        failures = self.invariant_failures()
        if len(failures) == 0: return

        raise RuntimeError(f"Following {len(failures)} invariants where violated:\n"
                           f"{textwrap.indent("\n".join(failures), " " * 4)}\n"
                           f"Context:\n"
                           f"{self.energy}\n"
                           f"{self.size}\n"
                           f"{list(self.boundary(Mode.BACKWARDS))}\n"
                           f"{list(self.boundary(Mode.FORWARDS))}")


def visualise_slice(sim: AdditiveSimulation, atomiser=lambda x, y: (x, y), crosshair=False, view_energies=False):
    width, height = shutil.get_terminal_size()
    margin = 3
    lattice = sim.graph
    assert isinstance(lattice, Lattice)

    def bg():
        if crosshair and (x == 0 or y == 0):
            print(end=Back.GREEN + " " + Back.RESET)
        else:
            print(end=" ")

    for y in range(-(height - margin) // 2, (height - margin) // 2):
        for x in range(-(width - margin) // 2, (width - margin) // 2):
            node = lattice.intern(atomiser(x, y))
            mode: Optional[Mode] = None
            energy = None

            for m in Mode:
                if node in sim.boundary(m):
                    mode = m
                    energy = sim.boundary(m).get_priority(node)

            if view_energies:
                if mode is None:
                    bg()
                else:
                    assert energy is not None
                    if energy < 0:
                        print(end=Fore.RED + str(-energy) + Fore.RESET)
                    else:
                        print(end=str(energy))
            else:
                match mode:
                    case Mode.BACKWARDS:
                        print(end=Fore.RED + "X" + Fore.RESET)
                    case Mode.FORWARDS:
                        print(end="O")
                    case None:
                        bg()
        print()

    print()


from messthaler_wulff._additive_simulation import OmniSimulation

from timeit import timeit
import tqdm
import random


def perf(func, number=1000_000):
    return timeit(func, number=number) / number * 1000 * 1000


def main():
    graph = Lattice(CommonLattice.fcc.value)
    sim = OmniSimulation(
        lambda x: graph.neighbors(x), lambda: graph.max_degree, 0
    )
    sim = AdditiveSimulation(graph)

    goal = 100_000
    if isinstance(sim, AdditiveSimulation):
        # 8 or 9 sec
        # 6 or 8 sec opt
        for i in tqdm.tqdm(range(goal)):
            node = random.choice(sim.next(Mode.FORWARDS))
            sim.move_to_boundary(node, Mode.FORWARDS)
    else:
        # 7 or 8 sec
        # 6 sec opt
        for i in tqdm.tqdm(range(goal)):
            sim.add_atom(random.randrange)

    # for i in range(1000):
    #     print(end=colorama.ansi.clear_screen(3))
    #     print(end=Cursor.POS(0,0))
    # node = random.choice(sim.next(Mode.FORWARDS))
    # sim.move_to_boundary(node, Mode.FORWARDS)
    # visualise_slice(sim)
    # input()


if __name__ == "__main__":
    main()
