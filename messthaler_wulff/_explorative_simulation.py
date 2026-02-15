import logging
import os
from typing import Optional

import colorama.ansi
import psutil
from colorama import Cursor
from prettytable import PrettyTable

from ._additive_simulation import OmniSimulation
from .abstract_crystal_store import TICrystal
from .advanced_simulation import DirectionalSimulation
from .decorators import wipe_screen
from .progress import debounce

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


class ExplorativeSimulation:
    def __init__(self, omni: OmniSimulation, goal: int,
                 require_energy: Optional[int] = None, bidi: bool = True, verbosity: int = 0, ti=True,
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
        self.verbosity = verbosity
        self.collect_crystals = collect_crystals
        if collect_crystals:
            self.crystals: list[list] = [list() for _ in range(self.nr_levels)]

        self.energies: list[int] = [2 ** 30] * self.nr_levels
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
            if self.verbosity >= 1:
                self.debug_print(self.verbosity)

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
    def debug_print(self, verbosity):
        if verbosity < 2:
            print(f"Total crystals: {sum(self.counts)}")
            return
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        total_memory_usage = mem_info.rss
        total_memory = psutil.virtual_memory().total

        wipe_screen()
        print(self)
        print(f"Stack size: {len(self.stack):,}; "
              f"Memory: {self.format_mem(total_memory_usage)}/{self.format_mem(total_memory)} "
              f"({total_memory_usage / total_memory:.2%})", flush=True)

    def __str__(self):
        table = PrettyTable(
            ["Atoms", "Minimal Energy", "Total Crystals", "Optimal Crystals"],
            align='r')
        table.custom_format = lambda f, v: f"{v:,}"

        for i in range(self.lower_bound, self.upper_bound + 1):
            d = self.data_index(i)

            table.add_row([i, self.energies[d], self.counts[d],
                           self.min_counts[d]])

        return str(table)
