import logging
from typing import Any

from messthaler_wulff._additive_simulation import OmniSimulation
from messthaler_wulff.abstract_crystal_store import DumbCrystal

log = logging.getLogger("messthaler_wulff")


class AdvancedSimulation:
    def __init__(self, omni: OmniSimulation):
        self.omni = omni
        self.abstract_crystal = DumbCrystal

        self.initial_state = self.abstract_crystal.wrap_atoms(omni.points())
        self.initial_atom_count = omni.atoms
        self.current_state = self.initial_state

        self.energies: dict[Any, int] = {}

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

    def previous_states(self, state):
        self.goto(state)
        for atom in self.omni.next_atoms(0):
            yield state.remove_atom(atom)

    def next_states(self, state):
        self.goto(state)
        for atom in self.omni.next_atoms(1):
            yield state.add_atom(atom)

    def set_atom(self, atom, direction):
        self.omni.force_set_atom(atom, direction)

        if direction == 1:
            self.current_state = self.current_state.add_atom(atom)
        else:
            self.current_state = self.current_state.remove_atom(atom)

    def goto(self, state):
        if state == self.current_state:
            return

        for direction, atom in self.current_state.diff(state):
            self.set_atom(atom, direction)

        assert self.current_state == state


class DirectionalSimulation:
    def __init__(self, omni: OmniSimulation, direction: int):
        self.sim = AdvancedSimulation(omni)
        self.initial_state = self.sim.initial_state
        self.initial_atom_count = self.sim.initial_atom_count
        self.direction = direction

    def previous_states(self, state):
        if self.direction == 1:
            yield from self.sim.previous_states(state)
        else:
            yield from self.sim.next_states(state)

    def next_states(self, state):
        if self.direction == 1:
            yield from self.sim.next_states(state)
        else:
            yield from self.sim.previous_states(state)

    def energy(self, state):
        return self.sim.energy(state)
