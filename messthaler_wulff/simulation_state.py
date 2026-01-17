import logging
from collections.abc import MutableSet, Callable, Iterable

from messthaler_wulff.additive_simulation import OmniSimulation

log = logging.getLogger("messthaler_wulff")


class TISortedSet(MutableSet):
    class TIIterator:

        def minus(self, p1, p2):
            return tuple(p1[i] - p2[i] for i in range(self.dimension + 1))

        def __init__(self, dimension: int, s):
            self.dimension = dimension
            self.minimum = s[0]
            self.set = s
            self.iter = iter(s)

        def __next__(self):
            return self.minus(next(self.iter), self.set[0])

    def __init__(self, dimension: int, s: MutableSet):
        self.dimension = dimension
        self.set = s

    def __iter__(self):
        return self.TIIterator(self.dimension, self.set)

    def add(self, value):
        self.set.add(value)

    def discard(self, value):
        self.set.discard(value)

    def __contains__(self, x):
        return x in self.set

    def __len__(self):
        return len(self.set)

    @classmethod
    def wrap(cls, dimension, set_type):
        return lambda i: cls(dimension, set_type(i))


class StupidCrystalHasher(Callable):
    def __call__(self, i: Iterable):
        return None


class SimpleCrystalHasher(Callable):
    def __init__(self, hash_function):
        self.hash_function = hash_function

    def __call__(self, i: Iterable):
        the_hash = self.hash_function()

        for atom in i:
            the_hash.update(str(atom).encode('utf-8'))

        return the_hash.hexdigest()


class CrystalNotHasher(Callable):
    def __call__(self, i: Iterable):
        return frozenset(i)


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
        return tuple(sorted(self.sim.omni.points()))


class AdvancedSimulation:
    def __init__(self, omni: OmniSimulation, atom_collection, hasher: Callable):
        self.omni = omni
        self.atoms = atom_collection(omni.points())
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
        return self.hasher(self.atoms)

    def next_atoms(self):
        return self.omni.next_atoms(OmniSimulation.FORWARDS)

    def add_atom(self, atom):
        self.omni.force_set_atom(atom, OmniSimulation.FORWARDS)
        self.state = self.state.add_atom(atom)
        self.atoms.add(atom)

    def pop_atom(self):
        if self.state == self.initial_state:
            raise ValueError("Can't pop atom if in empty state")
        atom = self.state.new_atom

        self.omni.force_set_atom(atom, OmniSimulation.BACKWARDS)
        self.state = self.state.parent
        self.atoms.discard(atom)

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
