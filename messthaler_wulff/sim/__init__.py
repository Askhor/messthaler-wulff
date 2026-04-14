import tqdm
from messthaler_wulff.datastructures.lattice import Lattice

from messthaler_wulff.data.common_lattices import CommonLattice
from messthaler_wulff.sim.crystal import Crystal
from messthaler_wulff.sim.energy import SurfaceEnergy
from messthaler_wulff.sim.guide import CrystalGuide
from messthaler_wulff.sim.quantity import CrystalQuantity

g = Lattice(CommonLattice.fcc.value)
c = Crystal(g)
q: CrystalQuantity = SurfaceEnergy(c)
guide = CrystalGuide(q, M)

for i in tqdm.tqdm(range(10_000_000)):
    c.toggle(0)
