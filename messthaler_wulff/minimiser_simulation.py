import logging
import math
from dataclasses import dataclass

from .additive_simulation import OmniSimulation
from .simulation_wrapper import SimulationState, SimulationInfo

log = logging.getLogger("messthaler_wulff")


# Data in the sense of this file is information about all 'global minimisers'
# like their minimal energy and how many there are

@dataclass(frozen=True)
class Data:
    count: int
    energy: int


class MinimiserSimulation:
    def __init__(self, omni_simulation: OmniSimulation):
        self.omni_simulation = omni_simulation
        self.initial_state = SimulationState(SimulationInfo.from_omni(omni_simulation))
        self.data_cache = [Data(1, 0)]

    def calc_data(self, n) -> Data:
        min_energy = math.inf
        count = 0

        for m in self.probable_minimisers(n):
            if m.energy < min_energy:
                count = 1
                min_energy = m.energy
            elif m.energy == min_energy:
                count += 1

        return Data(count, min_energy)

    def data(self, n) -> Data:
        while len(self.data_cache) < n + 1:
            self.data_cache.append(self.calc_data(len(self.data_cache)))

        return self.data_cache[n]

    def probable_minimisers(self, n):
        if n < 0:
            raise ValueError(f"n must be non-negative ({n})")

        if n == 0:
            yield self.initial_state
            return

        for m in self.minimisers(n - 1):
            for atom in m.next_atoms():
                yield m.add_atom(atom)

    def minimisers(self, n):
        if n < 0:
            raise ValueError(f"n must be non-negative ({n})")

        min_energy = self.data(n).energy
        visited = set()

        for m in self.probable_minimisers(n):
            if m.energy == min_energy:
                if m.hash() in visited:
                    continue
                visited.add(m.hash())
                yield m
