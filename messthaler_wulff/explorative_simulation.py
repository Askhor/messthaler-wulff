import logging
import math
from collections import defaultdict

from prettytable import PrettyTable

from . import free_monoid
from .additive_simulation import OmniSimulation
from .progress import debounce
from .simulation_state import AdvancedSimulation
from .terminal_formatting import wipe_screen

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


class ExplorativeSimulation:
    TEST_ENERGIES = [0, 12, 22, 30, 36, 44, 50, 54, 60, 66, 70, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120,
                     124, 126, 130, 134, 138, 142, 144, 148, 150, 154, 158, 160, 164, 166, 168, 168, 172, 176, 180, 184,
                     188, 192, 194, 198, 198, 202, 206, 210, 212, 216, 218, 222, 224, 224, 228, 230, 234, 238, 242, 244,
                     246, 246, 250, 250, 252, 256, 260, 264, 268, 268, 270, 270, 274, 276, 280, 282, 286, 286, 288, 288,
                     292, 296, 300, 302, 306, 306, 308, 308, 312]

    def __init__(self, omni: OmniSimulation, goal: int,
                 gm_mode: bool = False, bidi: bool = True, verbose=False, ti=True,
                 collect_crystals=False):
        self.sim = AdvancedSimulation(omni, OmniSimulation.FORWARDS if goal >= 0 else OmniSimulation.BACKWARDS, bidi)
        self.goal = abs(goal) + 1
        del goal
        self.bidi = bidi
        self.gm_mode = gm_mode
        self.ti = ti
        if ti:
            self.translations = defaultdict(dict)
        self.verbose = verbose
        self.collect_crystals = collect_crystals
        if collect_crystals:
            self.crystals = [list() for _ in range(self.goal)]

        self.energies = [math.inf] * self.goal
        self.counts = [0] * self.goal
        self.min_counts = [0] * self.goal

        self.visited = {self.sim.initial_state}
        self.stack = [self.sim.initial_state]

        self.run()

    def translate(self, primitive, minus):
        if minus in self.translations[primitive]:
            return self.translations[primitive][minus]
        elif primitive.length == 1:
            value = free_monoid.FreePrimitive.wrap_primitive(
                tuple(primitive.first[i] - minus[i] for i in range(len(minus))))
        else:
            value = self.translate(primitive.part_a, minus) + self.translate(primitive.part_b, minus)

        self.translations[primitive][minus] = value
        return value

    def canonical_translation(self, state):
        if state == ():
            return ()
        if isinstance(state, free_monoid.FreePrimitive):
            return self.translate(state, state.first)

        minus = state[-1].first
        return tuple(self.translate(primitive, minus) for primitive in state)

    def process_state(self, state):
        if self.ti:
            state = self.canonical_translation(state)
        if state in self.visited:
            return
        self.visited.add(state)
        self.stack.append(state)

    def run(self):
        sim = self.sim
        stack = self.stack

        while len(stack) > 0:
            if self.verbose:
                self.debug_print()

            state = stack.pop()

            count = sim.atom_count(state)
            new_energy = sim.energy(state)
            if self.gm_mode and new_energy > self.energies[count]:
                continue

            self.counts[count] += 1
            if new_energy < self.energies[count]:
                self.energies[count] = new_energy
                self.min_counts[count] = 1
                if self.collect_crystals:
                    self.crystals[count] = [state]
            elif new_energy == self.energies[count]:
                self.min_counts[count] += 1
                if self.collect_crystals:
                    self.crystals[count].append(state)

            if count >= self.goal - 1:
                continue

            for next_state in sim.next_states(state):
                self.process_state(next_state)
            if self.bidi:
                for prev_state in sim.previous_states(state):
                    self.process_state(prev_state)

    @debounce()
    def debug_print(self):
        wipe_screen()
        print(self)

    def __str__(self):

        table = PrettyTable(
            ["Atoms", "Minimal Energy", "Total Crystals", "Optimal Crystals", "Classic algorithm", "Comparison"],
            align='r')
        table.custom_format = lambda f, v: f"{v:,}"

        for i in range(self.goal):
            test_energy = "-"
            comparison = "-"
            if i < len(self.TEST_ENERGIES):
                test_energy = self.TEST_ENERGIES[i]
                comparison = sign(self.energies[i] - self.TEST_ENERGIES[i])

            table.add_row([i, self.energies[i], self.counts[i],
                           self.min_counts[i], test_energy, comparison])

        return str(table)


def sign(x):
    match x:
        case 0:
            return 0
        case _ if x > 0:
            return 1
        case _:
            return -1
