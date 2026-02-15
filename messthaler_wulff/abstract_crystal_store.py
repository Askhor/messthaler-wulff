import abc
from typing import Any


class AbstractCrystal(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def wrap_atom(cls, atom) -> 'AbstractCrystal': pass

    @classmethod
    def wrap_atoms(cls, atoms) -> 'AbstractCrystal':
        c = cls.empty()
        for atom in atoms:
            c = c.add_atom(atom)
        assert tuple(c.atoms()) == tuple(atoms)
        return c

    @classmethod
    @abc.abstractmethod
    def empty(cls) -> 'AbstractCrystal': pass

    @property
    @abc.abstractmethod
    def size(self) -> int: pass

    @abc.abstractmethod
    def add_atom(self, atom) -> 'AbstractCrystal': pass

    @abc.abstractmethod
    def remove_atom(self, atom) -> 'AbstractCrystal': pass

    @abc.abstractmethod
    def diff(self, other: 'AbstractCrystal'): pass

    @abc.abstractmethod
    def atoms(self): pass

    def first(self):
        return next(self.atoms())

    @abc.abstractmethod
    def __hash__(self) -> int: pass

    @abc.abstractmethod
    def __eq__(self, other: Any) -> bool: pass

    def __str__(self):
        return str(list(self.atoms()))


class TICrystal:
    def __init__(self, crystal: AbstractCrystal):
        if crystal.size != 0:
            self.minus = crystal.first()
        self.crystal = crystal

    def __hash__(self) -> int:
        if self.crystal.size == 0:
            return 324142
        m = self.minus
        return hash(tuple(tuple(a[i] - m[i] for i in range(len(a))) for a in self.crystal.atoms()))

    def __eq__(self, other: Any) -> bool:
        assert isinstance(other, TICrystal)
        if self.crystal.size == 0:
            return other.crystal.size == 0

        m1 = self.minus
        m2 = other.minus

        for a1, a2 in zip(self.crystal.atoms(), other.crystal.atoms()):
            for i in range(len(a1)):
                if a1[i] - m1[i] != a2[i] - m2[i]:
                    return False
        return True


class DumbCrystal(AbstractCrystal):
    def __init__(self, atoms: frozenset):
        self._atoms = atoms

    @classmethod
    def wrap_atom(cls, atom) -> 'AbstractCrystal':
        return cls(frozenset([atom]))

    @classmethod
    def empty(cls) -> 'AbstractCrystal':
        return cls(frozenset())

    @property
    def size(self) -> int:
        return len(self._atoms)

    def add_atom(self, atom) -> 'AbstractCrystal':
        return self.__class__(self._atoms | frozenset([atom]))

    def remove_atom(self, atom) -> 'AbstractCrystal':
        return self.__class__(self._atoms ^ frozenset([atom]))

    def diff(self, other: 'AbstractCrystal'):
        assert isinstance(other, DumbCrystal)
        for atom in self._atoms ^ other._atoms:
            yield 0 if atom in self._atoms else 1, atom

    def atoms(self):
        yield from sorted(self._atoms)

    def __hash__(self) -> int:
        return hash(self._atoms)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, DumbCrystal) and self._atoms == other._atoms

# class FMCrystal(AbstractCrystal):
#     def __init__(self, fm):
#         self.fm = fm
#         self._size = free_monoid.monoid_length(fm)
#
#     @classmethod
#     def wrap_atom(cls, atom):
#         return cls(free_monoid.FreePrimitive.wrap_primitive(atom))
#
#     @classmethod
#     def empty(cls):
#         return cls(())
#
#     @property
#     def size(self):
#         return self._size
#
#     def add_atom(self, atom):
#         return self.__class__(free_monoid.insert(self.fm, free_monoid.FreePrimitive.wrap_primitive(atom)))
#
#     def remove_atom(self, atom):
#         return self.__class__(free_monoid.remove(self.fm, atom))
#
#     def diff(self, other: 'AbstractCrystal'):
#         yield from free_monoid.diff(self.fm, other.fm)
#
#     def atoms(self):
#         yield from free_monoid.elements(self.fm)
#
#     def __hash__(self) -> int:
#         return hash(self.fm)
#
#     def __eq__(self, other: 'AbstractCrystal') -> bool:
#         return self.fm == other.fm
