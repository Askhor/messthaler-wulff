import hashlib
import logging
import math
from collections import defaultdict

from sortedcontainers import SortedSet

from .additive_simulation import OmniSimulation

log = logging.getLogger("messthaler_wulff")


class ExplorativeSimulation:
    def __init__(self, omni_simulation: OmniSimulation):
        self.omni_simulation = omni_simulation
        self.atoms = SortedSet()
        self.visited = set()

    def add_atom(self, atom):
        self.omni_simulation.force_set_atom(atom, OmniSimulation.FORWARDS)
        self.atoms.add(atom)

    def remove_atom(self, atom):
        self.omni_simulation.force_set_atom(atom, OmniSimulation.BACKWARDS)
        self.atoms.discard(atom)

    def compute_hash(self):
        the_hash = hashlib.sha256()

        for atom in self.atoms:
            the_hash.update(str(atom).encode('utf-8'))

        return the_hash.hexdigest()

    def recursive_explore(self, continue_predicate):
        the_hash = self.compute_hash()

        if the_hash in self.visited:
            return
        self.visited.add(the_hash)

        options = self.omni_simulation.next_atoms(OmniSimulation.FORWARDS)

        for atom in options:
            self.add_atom(atom)
            yield self.omni_simulation
            if continue_predicate(self.omni_simulation):
                yield from self.recursive_explore(continue_predicate)
            self.remove_atom(atom)

    def n_crystals(self, n: int):
        log.debug("Calculating n-Crystals")

        for state in self.recursive_explore(lambda sim: sim.atoms < n):
            if state.atoms == n:
                yield state


def crystal_data(simulation: OmniSimulation, max_n: int, callback):
    explorer = ExplorativeSimulation(simulation)
    min_energies = defaultdict(lambda: math.inf)
    crystal_counts = defaultdict(lambda: 0)

    for i, state in enumerate(explorer.recursive_explore(lambda sim: sim.atoms < max_n)):
        callback(min_energies, crystal_counts)

        crystal_counts[state.atoms] += 1

        if state.energy < min_energies[state.atoms]:
            min_energies[state.atoms] = state.energy

    return min_energies, crystal_counts
