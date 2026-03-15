from collections.abc import Sequence
from enum import Enum
from typing import Optional, Iterable, Any

from gooey.python_bindings.argparse_to_json import action_to_json

from messthaler_wulff.datastructures import HasInvariants
from messthaler_wulff.datastructures.defaultlist import defaultlist


class PriorityMode(Enum):
    MIN = -1, min
    MAX = 1, max

    def __init__(self, sign: int, function) -> None:
        super().__init__()
        self.sign = sign
        self.function = function


class PriorityLevel(list[int]):
    def my_add(self, value: int, indices: defaultlist[int]) -> None:
        indices[value] = len(self)
        self.append(value)

    def my_remove(self, value: int, indices: defaultlist[int]) -> None:
        index = indices[value]
        assert 0 <= index < len(self), f"Failed 0 <= {index} < {len(self)}"
        assert self[index] == value

        indices[value] = -1

        last = self.pop()

        if index != len(self):
            self[index] = last
            indices[last] = index


class PriorityStack(HasInvariants):
    """An implementation of a priority queue optimized for energy levels.
    Priorities are positive ints that are smaller than `priority_count` and
    values can only be ints."""

    def __init__(self, mode: PriorityMode, priority_count: int) -> None:
        self.extremal_key: Optional[int] = None
        self.mode = mode
        self.priority_levels: list[PriorityLevel] = [PriorityLevel() for _ in range(priority_count)]
        self.priorities: defaultlist[int] = defaultlist(-1)
        self.indices: defaultlist = defaultlist(-1)
        self.size: int = 0

    def extrema(self) -> Sequence[int]:
        assert self.extremal_key is not None
        return self.priority_levels[self.extremal_key]

    def __len__(self) -> int:
        return self.size

    def __contains__(self, value: int) -> bool:
        assert value >= 0
        return self.indices[value] != -1

    def _is_better(self, key1: int, key2: int) -> bool:
        """Is `key1` 'better' than `key2`"""
        sign = self.mode.sign
        return sign * key1 > sign * key2

    def __setitem__(self, value: int, key: int) -> None:
        assert 0 <= key < len(self.priority_levels)

        if self.extremal_key is None or self._is_better(key, self.extremal_key):
            self.extremal_key = key

        if value in self:
            old_key = self.priorities[value]
            if key == old_key:
                return
            old_level = self.priority_levels[old_key]
            old_level.my_remove(value, self.indices)
        else:
            self.size += 1

        new_level = self.priority_levels[key]
        new_level.my_add(value, self.indices)
        self.priorities[value] = key

        self._adjust_extremal_key()

        assert len(self) > 0

    def __delitem__(self, value: int):
        assert value in self
        self.size -= 1
        key = self.priorities[value]
        level = self.priority_levels[key]
        level.my_remove(value, self.indices)
        self.priorities[value] = -1
        self._adjust_extremal_key()

    def _adjust_extremal_key(self) -> None:
        if len(self) == 0:
            self.extremal_key = None
        else:
            assert self.extremal_key is not None
            while len(self.priority_levels[self.extremal_key]) <= 0:
                self.extremal_key -= self.mode.sign

    def select_levels(self, values: range) -> Iterable[int]:
        for i in values:
            yield from self.priority_levels[i]

    def invariant_failures(self) -> Iterable[str]:
        """Returns a list of strings of which invariants do
        not hold on this instance"""

        for key in range(len(self.priority_levels)):
            level = self.priority_levels[key]
            for value in level:
                if level[self.indices[value]] != value:
                    yield f"Value {value} not found at index {self.indices[value]} in level {key}"

        for value in range(len(self.indices)):
            key = self.priorities[value]
            index = self.indices[value]

            if (key == -1) != (index == -1):
                yield f"Priority and index are not in sync for {value}"
                continue

            if key == -1: continue
            if key >= len(self.priority_levels):
                yield (f"Priority {key} is "
                       f"too large for maximum "
                       f"{len(self.priority_levels)} (key: {key})")
                continue
            if index >= len(self.priority_levels[key]):
                yield (f"Priority level {key} "
                       f"is too short (key: {key})")
                continue

            if self.priority_levels[key][index] != value:
                yield f"{self.priority_levels[key][index]} does not match {value}"

    def invariant_violation_context(self) -> Iterable[Any]:
        def a(name: str):
            return name + ": " + str(getattr(self, name))

        yield a("extremal_key")
        yield a("priorities")
        yield a("indices")
        yield a("priority_levels")
