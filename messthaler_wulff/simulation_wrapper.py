import hashlib
from dataclasses import dataclass

from sortedcontainers import SortedSet

from messthaler_wulff.additive_simulation import OmniSimulation


@dataclass(frozen=True)
class SimulationInfo:
    omni_simulation: OmniSimulation
    atoms: SortedSet
    atom_stack: list
    visited: set

    def add_atom(self, atom):
        self.omni_simulation.force_set_atom(atom, OmniSimulation.FORWARDS)
        self.atom_stack.append(atom)
        self.atoms.add(atom)

    def pop_atom(self):
        atom = self.atom_stack.pop()
        self.omni_simulation.force_set_atom(atom, OmniSimulation.BACKWARDS)
        self.atoms.discard(atom)


class SimulationState:
    def __init__(self, sim: SimulationInfo):
        self.sim = sim

        self.atoms = omni_simulation.atoms
        self.energy = omni_simulation.energy
        self.hash = self.calc_hash()

    def calc_hash(self):
        the_hash = hashlib.sha256()

        for atom in self.sim.atoms:
            the_hash.update(str(atom).encode('utf-8'))

        return the_hash.hexdigest()

    def visited(self) -> bool:
        return self.hash in self.sim.visited
    
    def visit(self):
        self.sim.visited.add(self.hash)

    def goto(self):
        omni = self.sim.omni_simulation

        while omni.atoms > self.atoms:
            self.sim.pop_atom()

    def next_atoms(self):
        self.goto()
        return self.omni_simulation.next_atoms(OmniSimulation.FORWARDS)

    def add_atom(self, atom):
        self.goto()
        self.sim.add_atom(atom)

        return SimulationState(self.sim)
