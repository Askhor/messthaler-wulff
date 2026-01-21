import logging

from messthaler_wulff import free_monoid
from messthaler_wulff.additive_simulation import OmniSimulation

log = logging.getLogger("messthaler_wulff")


class AdvancedSimulation:
    def __init__(self, omni: OmniSimulation, direction: int, bidi: bool):
        self.omni = omni

        self.initial_state = free_monoid.from_string(sorted(omni.points()))
        self.initial_atom_count = omni.atoms
        self.current_state = self.initial_state

        self.direction = direction
        self.bidi = bidi

        self.energies = {}

    @staticmethod
    def cached(cache_name):
        def deco(function):
            def impl(self, state):
                cache = getattr(self, cache_name)
                if state in cache:
                    return cache[state]
                else:
                    value = function(self, state)
                    cache[state] = value
                    return value

            return impl

        return deco

    @cached("energies")
    def energy(self, state):
        self.goto(state)
        return self.omni.energy

    def atom_count(self, state):
        return free_monoid.monoid_length(state)

    def previous_states(self, state):
        self.goto(state)
        for atom in self.omni.next_atoms(1 - self.direction):
            yield free_monoid.remove(state, atom)

    def next_states(self, state):
        self.goto(state)
        for atom in self.omni.next_atoms(self.direction):
            yield self.add_atom(state, atom)

    @staticmethod
    def add_atom(state, atom):
        return free_monoid.insert(state, free_monoid.FreePrimitive.wrap_primitive(atom))

    def set_atom(self, atom, direction):
        """
        The direction here is relative to our direction
        """
        if self.direction == OmniSimulation.BACKWARDS:
            direction = 1 - direction

        self.omni.force_set_atom(atom, direction)

        if self.direction == direction:
            self.current_state = self.add_atom(self.current_state, atom)
        else:
            self.current_state = free_monoid.remove(self.current_state, atom)

    def goto(self, state: int):
        if state == self.current_state:
            return

        for direction, atom in free_monoid.diff(self.current_state, state):
            self.set_atom(atom, direction)

        assert self.current_state == state
