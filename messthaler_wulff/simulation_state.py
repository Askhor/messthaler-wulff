import hashlib
import logging
import math
from abc import ABC, abstractmethod

from sortedcontainers import SortedSet

from messthaler_wulff.additive_simulation import OmniSimulation

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


class CrystalHasher(ABC):
    @abstractmethod
    def add_atom(self, atom):
        pass

    @abstractmethod
    def remove_atom(self, atom):
        pass

    @abstractmethod
    def hash(self):
        pass


class SimpleCrystalHasher(CrystalHasher):
    def __init__(self, hash_function):
        self.atoms = SortedSet()
        self.hash_function = hash_function

    def add_atom(self, atom):
        self.atoms.add(atom)

    def remove_atom(self, atom):
        self.atoms.discard(atom)

    def hash(self):
        the_hash = self.hash_function()

        for atom in self.atoms:
            the_hash.update(str(atom).encode('utf-8'))

        return the_hash.hexdigest()

class TICrystalHasher(CrystalHasher):
    def __init__(self, dimension, hash_function):
        self.atoms = SortedSet()
        self.dimension = dimension
        self.hash_function = hash_function

    def add_atom(self, atom):
        self.atoms.add(atom)

    def remove_atom(self, atom):
        self.atoms.discard(atom)

    def hash(self):
        minima = [math.inf] * (self.dimension + 1)

        for atom in self.atoms:
            for i in range(self.dimension + 1):
                minima[i] = min(minima[i], atom[i])

        the_hash = self.hash_function()

        for atom in self.atoms:
            for i in range(self.dimension + 1):
                the_hash.update(str(atom[i] - minima[i]).encode('utf-8'))

        return the_hash.hexdigest()

class SimulationState:
    def __init__(self, sim, parent, new_atom):
        """
        This constructor is for internal use only
        """

        if parent is None:
            self.atom_count = 0
        else:
            self.atom_count = parent.atom_count + 1

        self.sim = sim
        self.parent = parent
        self.next_states = {}
        self.new_atom = new_atom

        self._energy = None
        self._hash = None

        if parent is None or new_atom is None:
            assert parent is None
            assert new_atom is None

    @classmethod
    def new_root(cls, sim):
        return cls(sim, None, None)

    def add_atom(self, atom):
        if atom not in self.next_states:
            self.next_states[atom] = SimulationState(self.sim, self, atom)

        return self.next_states[atom]

    @property
    def next_atoms(self):
        self.sim.goto(self)
        return self.sim.next_atoms()

    @property
    def energy(self):
        if self._energy is None:
            self.sim.goto(self)
            self._energy = self.sim.energy

        return self._energy

    @property
    def hash(self):
        if self._hash is None:
            self.sim.goto(self)
            self._hash = self.sim.hash

        return self._hash

    def __str__(self):
        if self.parent is None:
            assert self.new_atom is None
            return f"root"
        return f"{self.parent}->{self.new_atom}"

    def as_list(self):
        self.sim.goto(self)
        return list(sorted(self.sim.omni.points()))


class AdvancedSimulation:
    def __init__(self, omni: OmniSimulation, hasher: CrystalHasher):
        self.omni = omni
        self.hasher = hasher
        self.initial_state = SimulationState.new_root(self)
        self.state = self.initial_state

    @property
    def energy(self):
        return self.omni.energy

    @property
    def atom_count(self):
        return self.state.atom_count

    @property
    def hash(self):
        return self.hasher.hash()

    def next_atoms(self):
        return self.omni.next_atoms(OmniSimulation.FORWARDS)

    def add_atom(self, atom):
        self.omni.force_set_atom(atom, OmniSimulation.FORWARDS)
        self.state = self.state.add_atom(atom)
        self.hasher.add_atom(atom)

    def pop_atom(self):
        if self.state == self.initial_state:
            raise ValueError("Can't pop atom if in empty state")
        atom = self.state.new_atom

        self.omni.force_set_atom(atom, OmniSimulation.BACKWARDS)
        self.state = self.state.parent
        self.hasher.remove_atom(atom)

    def goto(self, state: SimulationState):

        atoms_to_add = []

        while self.atom_count > state.atom_count:
            self.pop_atom()

        while state.atom_count > self.atom_count:
            atoms_to_add.append(state.new_atom)
            state = state.parent

        while state != self.state:
            self.pop_atom()
            atoms_to_add.append(state.new_atom)
            state = state.parent

        while len(atoms_to_add) > 0:
            self.add_atom(atoms_to_add.pop())
