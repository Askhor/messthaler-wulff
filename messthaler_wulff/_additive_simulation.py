import shutil

from tqdm import tqdm

from .progress import ProgressBar


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
        assert self.energy >= 0
        reverse_boundary.set(atom, -mode_energy)
        if atom in mode_boundary:
            mode_boundary.unset(atom, mode_energy)

        for neighbor in self.neighborhood(atom):
            if neighbor in reverse_boundary:
                neighbor_energy = reverse_boundary.get(neighbor)
                new_energy = neighbor_energy + 2

                if self.energy_maximum() == new_energy:
                    reverse_boundary.unset(neighbor, neighbor_energy)
                    ...
                else:
                    reverse_boundary.set(neighbor, new_energy)
            elif neighbor in mode_boundary:
                neighbor_energy = mode_boundary.get(neighbor)
                new_energy = neighbor_energy - 2

                if self.energy_maximum() == new_energy:
                    mode_boundary.unset(neighbor, neighbor_energy)
                    ...
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

    def points(self):
        return self.boundaries[self.BACKWARDS].atoms()

    def fill(self, choice=lambda l: 0):
        for i in tqdm(range(100_000)):
            _, energy = self.boundaries[self.FORWARDS].minimum()
            if energy > 0:
                break
            self.add_atom(choice)

    def __str__(self):
        return "[" + ", ".join(map(str, sorted(self.points()))) + "]"
