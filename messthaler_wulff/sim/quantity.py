import abc

from messthaler_wulff.sim.crystal import CrystalLike, Crystal


class CrystalQuantity(CrystalLike):

    def __init__(self, crystal: Crystal, local_max: int, is_local: bool=False) -> None:
        super().__init__(crystal)
        self.local_max = local_max
        self.is_local = is_local

    @property
    @abc.abstractmethod
    def value(self) -> int:
        ...

    @abc.abstractmethod
    def local_value(self, atom: int) -> int:
        ...
