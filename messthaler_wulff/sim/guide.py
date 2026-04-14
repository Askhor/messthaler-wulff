from typing import Sequence

from messthaler_wulff.datastructures.priority_stack import PriorityMode, PriorityStack

from messthaler_wulff.sim.crystal import CrystalLike
from messthaler_wulff.sim.quantity import CrystalQuantity


class CrystalGuide(CrystalLike):
    def __init__(self, quantity: CrystalQuantity, mode: PriorityMode) -> None:
        super().__init__(quantity.crystal)
        self.quantity = quantity
        self.mode = mode
        self.stack = PriorityStack(mode, quantity.local_max)

    def next(self) -> Sequence[int]:
        return self.stack.extrema()

    def _toggle(self, atom: int) -> None:
        self.stack
