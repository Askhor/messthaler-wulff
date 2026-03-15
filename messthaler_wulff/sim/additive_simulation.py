import logging
import random
import shutil
import sys
import textwrap
from functools import partial
from typing import Iterable, Sequence, Optional

from colorama import Fore, Back

from messthaler_wulff.datastructures.defaultlist import defaultlist
from messthaler_wulff.datastructures.graph import Graph
from messthaler_wulff.datastructures.lattice import Lattice
from messthaler_wulff.datastructures.priority_stack import PriorityStack
from messthaler_wulff.decorators import compose
from messthaler_wulff.sim import crystal

log = logging.getLogger("messthaler_wulff")



# Old sim achieved 20_000 1/s

class AdditiveSimulation:
    """A blazingly fast simulation of crystals (subsets of a lattice/graph)
    and transformations (addition/removal) which locally minimize surface energy"""

    def __init__(self, graph: Graph) -> None:
        # self.energy = 0
        # r"""Current energy of the crystal defined by
        # $$
        #     E_{c} = \sum_{n \in c} f_{G \setminus c}(n)
        # $$"""
        # self.size = 0
        # """The number of atoms in the crystal"""
        # self.graph = graph
        # """The underlying graph used for the simulation"""
        #
        # self.f: defaultlist[int] = defaultlist(0)
        # self.χ_c: defaultlist[int] = defaultlist(0)
        self.boundaries = [PriorityStack(graph.max_degree + 1),
                           PriorityStack(graph.max_degree + 1)]
        # TODO
        self.boundary(Mode.FORWARDS).set_priority(
            Graph.ZERO,
            self.calculate_loneliness(Graph.ZERO, Mode.FORWARDS))

        # assert (self.boundary(Mode.FORWARDS).get_priority(Graph.ZERO)
        #         == self.calculate_loneliness(Graph.ZERO, Mode.FORWARDS))


    def energy_delta(self, node: int, mode: Mode) -> int:
        """Computes the energy delta between the current state and the current state but with `node`
        moved to the other boundary"""
        loneliness = self.boundary(mode).get_priority(node)
        return 2 * loneliness - self.graph.degree(node)

    def move_to_boundary(self, node: int, mode: Mode) -> None:
        """Updates this and neighboring nodes to have appropriate loneliness-scores after the move"""
        self.size += crystal.sign
        assert self.size >= 0

        mode_boundary = self.boundary(mode)
        reverse_boundary = self.reverse_boundary(mode)

        assert node in mode_boundary
        assert node not in reverse_boundary

        old_loneliness = mode_boundary.get_priority(node)
        neighbors = self.graph.neighbors(node)
        degree = len(neighbors)
        self.energy += self.energy_delta(node, mode)

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
        """Returns a sequence of nodes that represent locally optimal transformations"""
        return self.boundary(mode).minimums()

    def initialise(self, atoms: list[int]):
        """Can only be called if the simulation is empty. Will fill it with the specified atoms"""
        assert self.size == 0

        dups = list(duplicates(atoms))

        if len(dups) > 0:
            log.error(f"Initialising additive simulation failed because input data contains duplicate coordinate(s):\n"
                      f"{list(map(lambda x: self.graph.repr(x), dups))}")
            sys.exit(1)

        for a in atoms:
            self.boundary(Mode.FORWARDS).set_priority(a, self.graph.degree(a))
            assert a in self.boundary(Mode.FORWARDS)

        for a in atoms:
            assert a not in self.boundary(Mode.BACKWARDS)
            self.toggle(a)
            if a not in self.boundary(Mode.BACKWARDS):
                print(a)
                visualise_slice(self, lambda x, y: (x, y, 0))

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
        """Test the invariants checked by `invariant_failures` and raise a `RuntimeError` if any are violated"""
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


def fill(sim: AdditiveSimulation):
    """Add atoms to the simulation until the energy would increase"""
    while True:
        node = random.choice(sim.next(Mode.FORWARDS))
        if sim.energy_delta(node, Mode.FORWARDS) > 0:
            break
        sim.toggle(node)
