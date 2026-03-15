import abc
import textwrap
from abc import ABC
from typing import Iterable, Any


def duplicates[T](values: Iterable[T]) -> Iterable[T]:
    """Returns an iterable of all elements of `values` that are duplicates"""
    seen = set()
    dups = set()

    for value in values:
        if value in seen:
            if value not in dups:
                yield value
                dups.add(value)
        else:
            seen.add(value)


class Universe[T, Key](ABC):
    """Represents a context where every T has a canonical representation, the Key (usually int)"""

    @abc.abstractmethod
    def intern(self, rep: T) -> Key:
        """Get the canonical key for the representative"""
        ...

    @abc.abstractmethod
    def repr(self, node: Key) -> T:
        """Get the value that the key represents"""
        ...


class HasInvariants(ABC):
    @abc.abstractmethod
    def invariant_failures(self) -> Iterable[Any]:
        """Returns a list of strings of which invariants do
        not hold on this instance"""

    def invariant_violation_context(self) -> Iterable[Any]:
        yield "Nothing"

    def test_invariants(self) -> None:
        """Test the invariants checked by `invariant_failures` and raise a `RuntimeError` if any are violated"""
        failures = list(self.invariant_failures())
        if len(failures) == 0: return

        def block(values: Iterable[Any]) -> str:
            return textwrap.indent("\n".join(map(str, values)), " " * 4)

        raise RuntimeError(f"Following {len(failures)} invariants where violated:\n"
                           f"{block(failures)}\n"
                           f"Context:\n"
                           + block(self.invariant_violation_context()))
