import logging
import math
from dataclasses import dataclass

from .additive_simulation import OmniSimulation
from .simulation_state import CrystalHasher, AdvancedSimulation

log = logging.getLogger("messthaler_wulff")


@dataclass(frozen=True)
class Data:
    min_energy: int
    count: int


class MinimiserSimulation:
    def __init__(self, omni_simulation: OmniSimulation, hasher: CrystalHasher):
        self.sim = AdvancedSimulation(omni_simulation, hasher)

        self.cache = [Data(0, 1)]
        self.minimisers_cache = [(self.sim.initial_state,)]

    def calculate_data(self, n: int) -> Data:
        min_energy = math.inf
        count = 0

        for state in self.probable_minimisers(n):
            if state.energy < min_energy:
                count = 1
                min_energy = state.energy
            elif state.energy == min_energy:
                count += 1

        return Data(min_energy, count)

    def calculate_minimisers(self, n: int) -> tuple:
        min_energy = self.min_energy(n)
        minimisers = []
        visited = set()

        for state in self.probable_minimisers(n):
            if state.energy == min_energy:
                if state.hash in visited:
                    continue
                visited.add(state.hash)
                minimisers.append(state)

        return tuple(minimisers)

    def get_data(self, n) -> Data:
        while len(self.cache) < n + 1:
            self.cache.append(self.calculate_data(len(self.cache)))

        return self.cache[n]

    def probable_minimisers(self, n):
        if n <= 0:
            raise ValueError(f"n must be positive ({n})")

        for state in self.minimisers(n - 1):
            for atom in state.next_atoms:
                yield state.add_atom(atom)

    def minimisers(self, n):
        if n < 0:
            raise ValueError(f"n must be non-negative ({n})")

        while len(self.minimisers_cache) < n + 1:
            self.minimisers_cache.append(self.calculate_minimisers(len(self.minimisers_cache)))

        return self.minimisers_cache[n]

    def min_energy(self, n):
        return self.get_data(n).min_energy

    def minimiser_count(self, n: int):
        return self.get_data(n).count
