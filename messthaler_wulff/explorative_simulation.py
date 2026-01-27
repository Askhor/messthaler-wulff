import logging
import math
import os

import psutil
from prettytable import PrettyTable

from .abstract_crystal_store import TICrystal
from .additive_simulation import OmniSimulation
from .advanced_simulation import DirectionalSimulation
from .progress import debounce
from .terminal_formatting import wipe_screen

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


class ExplorativeSimulation:
    TEST_ENERGIES: list[int] = [0, 12, 22, 30, 36, 44, 50, 54, 60, 66, 70, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112,
                                116, 120, 124, 126, 130, 134, 138, 142, 144, 148, 150, 154, 158, 160, 164, 166, 168,
                                168, 172, 176, 180, 184, 188, 192, 194, 198, 198, 202, 206, 210, 212, 216, 218, 222,
                                224, 224, 228, 230, 234, 238, 242, 244, 246, 246, 250, 250, 252, 256, 260, 264, 268,
                                268, 270, 270, 274, 276, 280, 282, 286, 286, 288, 288, 292, 296, 300, 302, 306, 306,
                                308, 308, 312]

    def __init__(self, omni: OmniSimulation, goal: int,
                 require_energy: int = None, bidi: bool = True, verbose=False, ti=True,
                 collect_crystals=False):
        self.initial_count = omni.atoms
        self.direction_sign = 1 if goal >= self.initial_count else -1
        log.debug(f"Going in direction {self.direction_sign}")
        self.upper_bound = max(goal, self.initial_count)
        self.lower_bound = min(goal, self.initial_count)
        self.nr_levels = self.upper_bound - self.lower_bound + 1

        self.sim = DirectionalSimulation(omni,
                                         1 if goal >= self.initial_count else 0)

        self.bidi = bidi
        self.require_energy = require_energy
        self.ti = ti
        self.verbose = verbose
        self.collect_crystals = collect_crystals
        if collect_crystals:
            self.crystals: list[list] = [list() for _ in range(self.nr_levels)]

        self.energies: list[int] = [math.inf] * self.nr_levels
        self.counts = [0] * self.nr_levels
        self.min_counts = [0] * self.nr_levels

        self.visited = {self.sim.initial_state}
        self.stack = [self.sim.initial_state]

        self.run()

    def data_index(self, i: int) -> int:
        return abs(i - self.initial_count)

    @classmethod
    def canonical_translation(cls, state):
        return TICrystal(state)

    def visit_state(self, state) -> bool:
        if self.ti:
            state = self.canonical_translation(state)
        if state in self.visited:
            return False
        self.visited.add(state)
        return True

    def process_state(self, state):
        if self.visit_state(state):
            self.stack.append(state)

    def run(self):
        sim = self.sim
        stack = self.stack

        while len(stack) > 0:
            if self.verbose:
                self.debug_print()

            state = stack.pop()

            i = state.size
            d = self.data_index(i)

            assert 0 <= d < self.nr_levels

            new_energy = sim.energy(state)
            if self.require_energy is not None and new_energy > self.energies[d] + self.require_energy:
                continue

            self.counts[d] += 1

            if new_energy < self.energies[d]:
                self.energies[d] = new_energy
                self.min_counts[d] = 1
                if self.collect_crystals:
                    self.crystals[d] = [state]
            elif new_energy == self.energies[d]:
                self.min_counts[d] += 1
                if self.collect_crystals:
                    self.crystals[d].append(state)

            if self.bidi and d > 0:
                for prev_state in sim.previous_states(state):
                    self.process_state(prev_state)
            if d < self.nr_levels - 1:
                for next_state in sim.next_states(state):
                    self.data_index(next_state.size)
                    self.process_state(next_state)

    @staticmethod
    def format_mem(m):
        exponent = 0
        while m >= 1000 and exponent < 3:
            m /= 1000
            exponent += 1

        postfix = ["B", "KB", "MB", "GB"][exponent]

        return f"{m:.1f} {postfix}"

    @debounce()
    def debug_print(self):
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        total_memory_usage = mem_info.rss

        wipe_screen()
        print(self)
        print(f"Stack size: {len(self.stack):,}; Memory: {self.format_mem(total_memory_usage)}")

    def comparison(self, i: int) -> int:
        return self.energies[self.data_index(i)] - self.TEST_ENERGIES[i]

    def __str__(self):
        table = PrettyTable(
            ["Atoms", "Minimal Energy", "Total Crystals", "Optimal Crystals", "Classic algorithm", "Comparison"],
            align='r')
        table.custom_format = lambda f, v: f"{v:,}"

        for i in range(self.lower_bound, self.upper_bound + 1):
            d = self.data_index(i)
            test_energy = math.nan
            comparison = math.nan
            if i < len(self.TEST_ENERGIES):
                test_energy = self.TEST_ENERGIES[i]
                comparison = self.comparison(i)

            table.add_row([i, self.energies[d], self.counts[d],
                           self.min_counts[d], test_energy, comparison])

        return str(table)
