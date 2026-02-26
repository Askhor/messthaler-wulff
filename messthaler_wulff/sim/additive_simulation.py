import logging
import random
import shutil
import sys
import textwrap
from enum import Enum
from functools import partial
from typing import Iterable, Sequence, Optional

from colorama import Fore, Back

from messthaler_wulff.decorators import compose
from messthaler_wulff.graph import Graph, Lattice
from messthaler_wulff.datastructures.priority_stack import PriorityStack

log = logging.getLogger("messthaler_wulff")


class Mode(Enum):
    BACKWARDS = 0, -1
    FORWARDS = 1, 1

    def __init__(self, index: int, sign: int):
        super().__init__()
        self.index = index
        """The mathematical equivalent of this value. Forwards
        is assigned 1 in the theory and backwards 0."""
        self.sign = sign
        """1 for forwards and -1 for backwards"""

    def __str__(self):
        return self.name[0]

    def __repr__(self):
        return str(self)


class AdditiveSimulation:
    """A blazingly fast simulation of crystals (subsets of a lattice/graph)
    and transformations (addition/removal) which locally minimize surface energy"""

    def __init__(self, graph: Graph) -> None:
        self.energy = 0
        r"""Current energy of the crystal defined by
        $$
            \xi_{C_0} = \sum_{n \in C_0} l_n^1
        $$"""
        self.size = 0
        """The number of atoms in the crystal"""
        self.graph = graph
        """The underlying graph used for the simulation"""

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
        r"""Calculates the loneliness according to $l_n^i = \\# \\{ n_0 \in \eta(n) \mid n_0 \in C_i \\}$,
        where `node` is $n$ and `mode.index` is $i$.
        """
        energy = self.graph.degree(node)
        reverse_boundary = self.reverse_boundary(mode)

        for neighbor in self.graph.neighbors(node):
            if neighbor in reverse_boundary:
                energy -= 1

        return energy

    def toggle(self, node: int) -> None:
        """Calls move_to_boundary with the appropriate mode, resulting in a toggle between boundaries."""
        mode: Mode
        if node in self.boundary(Mode.FORWARDS):
            mode = Mode.FORWARDS
        else:
            mode = Mode.BACKWARDS

        self.move_to_boundary(node, mode)

    def energy_delta(self, node: int, mode: Mode) -> int:
        """Computes the energy delta between the current state and the current state but with `node`
        moved to the other boundary"""
        loneliness = self.boundary(mode).get_priority(node)
        return 2 * loneliness - self.graph.degree(node)

    def move_to_boundary(self, node: int, mode: Mode) -> None:
        """Updates this and neighboring nodes to have appropriate loneliness-scores after the move"""
        self.size += mode.sign
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


def duplicates[T](values: Iterable[T]) -> Iterable[T]:
    """Returns an iterable of all elements of `values` that are duplicates"""
    seen = set()
    dups = set()

    for value in values:
        if value in seen:
            if value not in dups:
                yield value
                dups.add(value)
        else:
            seen.add(value)


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
