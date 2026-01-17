import logging
import math

from .additive_simulation import OmniSimulation
from .simulation_state import CrystalHasher, AdvancedSimulation

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


def hacky_cache(cache_name):
    def deco(function):
        def impl(self, n: int):
            cache = getattr(self, cache_name)
            while len(cache) < n + 1:
                cache.append(function(self, len(cache)))

            return cache[n]

        return impl

    return deco


class MinimiserSimulation:
    def __init__(self, omni_simulation: OmniSimulation, hasher: CrystalHasher):
        self.sim = AdvancedSimulation(omni_simulation, hasher)

        self.min_energy_cache = [0]
        self.count_cache = [1]
        self.minimisers_cache = [(self.sim.initial_state,)]

    def probable_minimisers(self, n):
        if n <= 0:
            raise ValueError(f"n must be positive ({n})")

        for state in self.minimisers(n - 1):
            for atom in state.next_atoms:
                yield state.add_atom(atom)

    @hacky_cache("minimisers_cache")
    def minimisers(self, n):
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

    @hacky_cache("min_energy_cache")
    def min_energy(self, n):
        min_energy = math.inf

        for state in self.probable_minimisers(n):
            if state.energy < min_energy:
                min_energy = state.energy

        return min_energy

    @hacky_cache("count_cache")
    def minimiser_count(self, n: int):

        return len(self.minimisers(n))
