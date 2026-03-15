from messthaler_wulff.datastructures.defaultlist import defaultlist
from messthaler_wulff.sim.crystal import Crystal, sign
from messthaler_wulff.sim.quantity import CrystalQuantity


class SurfaceEnergy(CrystalQuantity):
    def __init__(self, crystal: Crystal):
        super().__init__(crystal, crystal.graph.max_degree, is_local=True)

        self.energy = 0
        r"""Current energy of the crystal defined by
                $$
                    E_{c} = \sum_{n \in c} f_{G \setminus c}(n)
                $$"""
        self.f: defaultlist[int] = defaultlist(0)

    def calc_f(self, node: int) -> int:
        x_c = self.crystal.x_c
        f = 0

        for neighbor in self.graph.neighbors(node):
            f += x_c[neighbor]

        return f

    @property
    def value(self) -> int:
        return self.energy

    def local_value(self, atom: int) -> int:
        return self.f[atom]

    def _toggle(self, atom: int) -> None:
        delta = sign(self.crystal.x_c[atom])
        graph = self.graph

        for n in graph.neighbors(atom):
            self.f[n] -= delta

        self.energy += delta * (2 * self.f[atom] - graph.degree(atom))
