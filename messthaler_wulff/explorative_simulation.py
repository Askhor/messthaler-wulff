import hashlib
import logging

from sortedcontainers import SortedSet

from .additive_simulation import OmniSimulation

log = logging.getLogger("messthaler_wulff")


class ExplorativeSimulation:

    def __init__(self, omni_simulation: OmniSimulation):
        self.omni_simulation = omni_simulation
        self.atoms = SortedSet()
        self.visited = set()
        self.atom_stack = []
        self.options_stack = []

    def compute_hash(self):
        the_hash = hashlib.sha256()

        for atom in self.atoms:
            the_hash.update(str(atom).encode('utf-8'))

        return the_hash.hexdigest()

    # def explore(self, continue_predicate):
    #
    #     while True:
    #         if len(self.options_stack) == 0:
    #
    #         if len(self.options_stack[-1]) == 0:
    #             self.options_stack.pop()
    #             newest_atom = self.atom_stack.pop()
    #             self.omni_simulation.force_set_atom(newest_atom, OmniSimulation.BACKWARDS)
    #         else:
    #             next_atom = self.options_stack[-1].pop()

    def recursive_explore(self, continue_predicate):
        options = self.omni_simulation.next_atoms(OmniSimulation.FORWARDS)

        for atom in options:
            self.omni_simulation.force_set_atom(atom, OmniSimulation.FORWARDS)
            yield self.omni_simulation
            if continue_predicate(self.omni_simulation):
                yield from self.recursive_explore(continue_predicate)
            self.omni_simulation.force_set_atom(atom, OmniSimulation.BACKWARDS)

    def n_crystals(self, n: int):
        log.debug("Calculating n-Crystals")
        yield from self.recursive_explore(lambda sim: sim.atoms < n)
