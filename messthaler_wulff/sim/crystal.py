import abc
from typing import override

from messthaler_wulff.datastructures.defaultlist import defaultlist
from messthaler_wulff.datastructures.graph import Graph


def sign(x: int) -> int:
    """Maps 0 to -1 and 1 to 1"""
    return 2 * x - 1


class CrystalLike(abc.ABC):
    def __init__(self, crystal: "Crystal", auto_register: bool = True) -> None:
        self.crystal = crystal
        if auto_register:
            self.crystal.register(self)
        self.graph: Graph = self.crystal.graph

    @abc.abstractmethod
    def _toggle(self, atom: int) -> None:
        """Toggle a node in the graph"""
        ...


class Crystal(CrystalLike):
    def __init__(self, graph: Graph) -> None:
        self.size = 0
        self.graph = graph
        self.x_c: defaultlist[int] = defaultlist(0)
        """This is a list of values for every node in the graph. It is 0 if the node is not
                in the crystal and 1 otherwise."""
        self._crystal_likes: list[CrystalLike] = []
        self._is_running = False
        super().__init__(self, auto_register=False)

    def __contains__(self, atom: int):
        return self.x_c[atom] == 1

    def toggle(self, atom: int) -> None:
        self._is_running = True

        for cl in self._crystal_likes:
            cl._toggle(atom)
        self._toggle(atom)

    def register(self, crystal_like: CrystalLike) -> None:
        assert not self._is_running
        self._crystal_likes.append(crystal_like)

    @override
    def _toggle(self, atom: int):
        self.size -= sign(self.x_c[atom])
        self.x_c[atom] = 1 - self.x_c[atom]
