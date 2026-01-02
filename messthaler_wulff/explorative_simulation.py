import logging
import math
from dataclasses import dataclass

from .additive_simulation import OmniSimulation
from .simulation_state import CrystalHasher, AdvancedSimulation

log = logging.getLogger("messthaler_wulff")


@dataclass(frozen=True)
class Data:
    crystals: tuple
    min_energy: int
    count: int


class ExplorativeSimulation:
    def __init__(self, omni: OmniSimulation, hasher: CrystalHasher):
        self.sim = AdvancedSimulation(omni, hasher)

        self.cache = [Data((self.sim.initial_state,), 0, 1)]

    def calculate_data(self, n: int) -> Data:
        visited = set()
        crystals = []
        min_energy = math.inf
        count = 0

        for state in self.crystals(n - 1):
            for atom in state.next_atoms:
                new_state = state.add_atom(atom)
                if new_state.hash in visited:
                    continue

                visited.add(new_state.hash)
                min_energy = min(min_energy, new_state.energy)
                count += 1
                crystals.append(new_state)

        return Data(tuple(crystals), min_energy, count)

    def get_data(self, n: int):
        while len(self.cache) < n + 1:
            self.cache.append(self.calculate_data(len(self.cache)))

        return self.cache[n]

    def crystals(self, n: int):
        return self.get_data(n).crystals

    def min_energy(self, n: int):
        return self.get_data(n).min_energy

    def crystal_count(self, n: int):
        return self.get_data(n).count
