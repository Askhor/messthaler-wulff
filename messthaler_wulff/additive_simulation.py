import json
import random
import shutil
import time
from collections import defaultdict

import numpy as np

from .progress import ProgressBar


class EnergyTracker:
    class EnergyLevel:
        def __init__(self):
            self.values = []
            self.indices = {}

        def __len__(self):
            return len(self.values)

        def __getitem__(self, i):
            return self.values[i]

        def add(self, atom):
            if atom in self.indices:
                return

            self.indices[atom] = len(self.values)
            self.values.append(atom)

        def remove(self, atom):
            if len(self.values) == 0:
                raise ValueError("I am empty")

            index = self.indices[atom]
            try:
                if index == len(self.values) - 1:
                    self.values.pop()
                else:
                    self.values[index] = self.values.pop()
                    self.indices[self.values[index]] = index
            except IndexError:
                raise IndexError(f"List index {index} out of range for {self.values}")

            del self.indices[atom]

        def __str__(self):
            return str(len(self.values))

        def __repr__(self):
            return str(self)

        def __iter__(self):
            for i in range(len(self)):
                yield self[i]

        def json_obj(self):
            return [str(v) for v in self.values]  # f"{len(self.values)} values"

    def __init__(self):
        self.min_energy = None
        self.energy_levels = defaultdict(EnergyTracker.EnergyLevel)
        self.atom2energy = {}

    def minimum(self, choice=lambda x: 0):
        level = self.energy_levels[self.min_energy]
        atom = level[choice(len(level))]
        return atom, self.min_energy

    def all_minimums(self):
        level = self.energy_levels[self.min_energy]
        return list(level)

    def __len__(self):
        return len(self.atom2energy)

    def __contains__(self, atom):
        return atom in self.atom2energy

    def get(self, atom):
        return self.atom2energy[atom]

    def set(self, atom, energy):
        if self.min_energy is None or energy < self.min_energy:
            self.min_energy = energy

        if atom in self.atom2energy:
            old_energy = self.atom2energy[atom]
            if old_energy != energy:
                old_level = self.energy_levels[old_energy]
                old_level.remove(atom)
                level = self.energy_levels[energy]
                level.add(atom)
                self.adjust_min_energy()

            self.atom2energy[atom] = energy
        else:
            level = self.energy_levels[energy]
            level.add(atom)
            self.atom2energy[atom] = energy

    def unset(self, atom, energy):
        level = self.energy_levels[energy]
        level.remove(atom)
        del self.atom2energy[atom]

        self.adjust_min_energy()

    def adjust_min_energy(self):
        if len(self) == 0:
            self.min_energy = None
        else:
            while len(self.energy_levels[self.min_energy]) <= 0:
                self.min_energy += 1

    def atoms(self):
        return self.atom2energy.keys()

    def __str__(self):
        return json.dumps({
            "min_energy": self.min_energy,
            "atom2energy": {
                str(k): v for (k, v) in self.atom2energy.items()},
            "energy_levels": {
                k: v.json_obj() for (k, v) in self.energy_levels.items()
            }
        }, indent=4)


class OmniSimulation:
    BACKWARDS = 0
    FORWARDS = 1

    def __init__(self, neighborhood, energy_maximum=None, origin=(0, 0, 0, 0)):
        if energy_maximum is None:
            energy_maximum = neighborhood.energy_maximum

        self.energy = 0
        self.atoms = 0
        self.neighborhood = neighborhood
        self.energy_maximum = energy_maximum

        self.boundaries = [EnergyTracker(), EnergyTracker()]
        self.boundaries[self.FORWARDS].set(origin, self.calculate_energy(origin, mode=self.FORWARDS))

    def calculate_energy(self, atom, mode):
        energy = 0

        for neighbor in self.neighborhood(atom):
            energy += -1 if neighbor in self.boundaries[1 - mode] else 1

        return energy

    def set_atom(self, atom, energy, mode):
        mode_boundary = self.boundaries[mode]
        reverse_boundary = self.boundaries[1 - mode]

        mode_energy = energy
        self.energy += mode_energy
        reverse_boundary.set(atom, -mode_energy)
        if atom in mode_boundary:
            mode_boundary.unset(atom, mode_energy)

        for neighbor in self.neighborhood(atom):
            if neighbor in reverse_boundary:
                neighbor_energy = reverse_boundary.get(neighbor)
                new_energy = neighbor_energy + 2

                if self.energy_maximum() == new_energy:
                    reverse_boundary.unset(neighbor, neighbor_energy)
                else:
                    reverse_boundary.set(neighbor, new_energy)
            elif neighbor in mode_boundary:
                neighbor_energy = mode_boundary.get(neighbor)
                new_energy = neighbor_energy - 2

                if self.energy_maximum() == new_energy:
                    mode_boundary.unset(neighbor, neighbor_energy)
                else:
                    mode_boundary.set(neighbor, new_energy)
            else:
                mode_boundary.set(neighbor, self.calculate_energy(neighbor, mode))

    def next_atom(self, choice, mode):
        return self.boundaries[mode].minimum(choice)

    def next_atoms(self, mode):
        return self.boundaries[mode].all_minimums()

    def adjust_atom_count(self, mode):
        if mode == self.BACKWARDS and self.atoms <= 0:
            raise ValueError("No atoms left, so can't remove one")

        match mode:
            case self.FORWARDS:
                self.atoms += 1
            case self.BACKWARDS:
                self.atoms -= 1

    def add_atom(self, choice=lambda l: 0):
        self.adjust_atom_count(self.FORWARDS)

        atom, energy = self.next_atom(choice, self.FORWARDS)
        self.set_atom(atom,
                      energy,
                      self.FORWARDS)

    def remove_atom(self, choice=lambda l: 0):
        self.adjust_atom_count(self.BACKWARDS)

        atom, energy = self.next_atom(choice, self.BACKWARDS)
        self.set_atom(atom,
                      energy,
                      self.BACKWARDS)

    def force_set_atom(self, atom, mode=FORWARDS):
        self.adjust_atom_count(mode)

        atom2energy = self.boundaries[mode].atom2energy
        if atom in atom2energy:
            energy = atom2energy[atom]
        else:
            energy = self.calculate_energy(atom, mode)
        self.set_atom(atom, energy, mode)

    def visualise_slice(self, atomiser=lambda x, y: (0, x, y), crosshair=False, view_energies=False, color=True):
        width, height = shutil.get_terminal_size()
        margin = 3
        fg_red = "\x1b[38;2;200;0;0;1m" if color else ""
        bg_green = "\x1b[48;2;0;70;0;1m" if color else ""
        unset = "\x1b[m" if color else ""

        def bg():
            if crosshair and (x == 0 or y == 0):
                print(end=bg_green + " " + unset)
            else:
                print(end=" ")

        for y in range(-(height - margin) // 2, (height - margin) // 2):
            for x in range(-(width - margin) // 2, (width - margin) // 2):
                atom = atomiser(x, y)
                mode = -1
                energy = None

                for m in range(2):
                    if atom in self.boundaries[m]:
                        mode = m
                        energy = self.boundaries[m].get(atom)

                if view_energies:
                    if mode == -1:
                        bg()
                    elif energy < 0:
                        print(end=fg_red + str(-energy) + unset)
                    else:
                        print(end=str(energy))
                else:
                    match mode:
                        case self.BACKWARDS:
                            print(end=fg_red + "X" + unset)
                        case self.FORWARDS:
                            print(end="O")
                        case _:
                            bg()
            print()

        print()

    def interactive(self, dimension=2, color=True):
        z = 0
        view_energies = False
        crosshair = False
        atomiser = None
        match dimension:
            case 1:
                atomiser = lambda x, y: (0, x)
            case 2:
                atomiser = lambda x, y: (0, x, y)
            case 3:
                atomiser = lambda x, y: (0, x, y, z)
            case _:
                raise ValueError(f"Unsupported dimension: {dimension}")

        def set_cmd(method):
            try:
                if len(args) > 0:
                    goal = int(args[0])
                    progress = ProgressBar(goal, lambda: self.energy)
                    for i in range(goal):
                        progress(i)
                        method(lambda l: random.randrange(l))
                else:
                    method(lambda l: random.randrange(l))
            except (ValueError, TypeError):
                pass

        try:
            while True:
                wipe_screen()
                self.visualise_slice(atomiser, crosshair=crosshair, view_energies=view_energies, color=color)
                print(f"Number of atoms: {self.atoms}; Total energy: {self.energy}; Z-Layer: {z}")

                try:
                    cmd, *args = input("Input Command: (add, rm, up, down, exit, ?) ").split()
                except ValueError:
                    continue

                match (cmd.lower()):
                    case "add":
                        set_cmd(self.add_atom)
                    case "rm":
                        set_cmd(self.remove_atom)
                    case "up":
                        z += 1
                    case "down":
                        z -= 1
                    case "layer":
                        if len(args) > 0:
                            z = int(args[0])
                    case "energy":
                        view_energies = not view_energies
                    case "forwards":
                        print(self.boundaries[self.FORWARDS])
                        input("Press Enter to continue")
                    case "backwards":
                        print(self.boundaries[self.BACKWARDS])
                        input("Press Enter to continue")
                    case "crosshair":
                        crosshair = not crosshair
                    case "fill":
                        self.fill(lambda l: random.randrange(l))
                    case "exit":
                        break
                    case "?":
                        input("""
add         - Adds the next atom in the sequence
rm          - Removes the next atom in the reverse sequence
up          - Goes up one z-layer (if possible)
down        - Goes down one z-layer (if possible)
energy      - Toggle the energy view mode
forwards    - Display the forwards boundary energy tracker
backwards   - Display the backwards boundary energy tracker
crosshair   - Enable a crosshair
fill        - Adds atoms to the crystal until the energy would increase
exit        - Exit interactive mode
?           - Displays this help

Press Enter to continue execution
""")

        except (ValueError, TypeError):
            self.interactive(dimension=dimension, color=color)
        except KeyboardInterrupt:
            print()

    def points(self):
        return self.boundaries[self.BACKWARDS].atoms()

    def fill(self, choice=lambda l: 0):
        while True:
            atom, energy = self.next_atom(choice, self.FORWARDS)
            if energy > 0:
                break

            self.adjust_atom_count(self.FORWARDS)

            self.set_atom(atom,
                          energy,
                          self.FORWARDS)


def wipe_screen():
    print(f"\x1b[3J\x1b[H\x1b[J", end="")


def move(atom, offset):
    return tuple((atom[0], *(atom[i + 1] + offset[i] for i in range(len(atom) - 1))))


class SimpleNeighborhood:
    def __init__(self, transform: np.ndarray):
        start = time.time()
        shape = transform.shape
        self.transform = transform
        self.n = shape[0]
        if shape[0] != shape[1]:
            raise ValueError("I need a square matrix")

        self.base_neighborhood = set()

        self.find_neighbors()

        print(f"Calculated in {time.time() - start:.2f} seconds neighbors for:\n{transform}")
        print(f"Neighbors are: {self.base_neighborhood}")
        print()

    @staticmethod
    def points_within_dist(n, dist):
        if n == 0:
            yield ()
            return
        if n == 1:
            for i in list(range(-dist, dist + 1)):
                yield (i,)
            return

        for i in range(-dist, dist + 1):
            for p in SimpleNeighborhood.points_within_dist(n - 1, dist):
                yield [*p, i]

    @staticmethod
    def points_with_dist(n, dist):
        if dist == 0:
            yield [0] * n
            return
        if dist == 1:
            for p in SimpleNeighborhood.points_within_dist(n, dist):
                if all(x == 0 for x in p): continue
                yield p
            return

        for i in range(n):
            for sign in [-1, 1]:
                for p in SimpleNeighborhood.points_within_dist(n - 1, dist):
                    yield *p[:i], sign * dist, *p[i:]

    def find_neighbors(self):
        for dist in range(1, 10):
            changed = 0

            for p in SimpleNeighborhood.points_with_dist(self.n, dist):
                point = np.dot(self.transform, np.array(p))
                if np.linalg.norm(point) <= 1:
                    p = tuple(p)
                    if p not in self.base_neighborhood:
                        self.base_neighborhood.add(p)
                        changed += 1

            if changed == 0:
                return

        raise RuntimeError("Could not find all neighbors")

    def __call__(self, pos):
        return [move(pos, x) for x in self.base_neighborhood]

    def energy_maximum(self):
        return len(self.base_neighborhood)


def main():
    OmniSimulation(SimpleNeighborhood(np.identity(2)), None, (0, 0, 0)).interactive(2)


if __name__ == "__main__":
    main()
