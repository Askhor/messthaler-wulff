import textwrap
from functools import partial
from typing import Optional, Iterable, Callable, Iterator

from messthaler_wulff.decorators import compose

type Priority = int
type Key = int
type PriorityLevel = list[Key]


class defaultlist[T]:
    def __init__(self, default: Callable[..., T]):
        self.default: Callable[..., T] = default
        self.values: list[T] = list()

    def _ensure_capacity(self, key: int):
        l = self.values
        while len(l) <= key:
            l.append(self.default())

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key: int) -> T:
        self._ensure_capacity(key)
        return self.values[key]

    def __setitem__(self, key: int, value: T) -> None:
        self._ensure_capacity(key)
        self.values[key] = value

    def __str__(self):
        return str(self.values)


class PriorityStack:
    """An implementation of a priority queue optimized for energy levels"""

    def __init__(self, priority_count) -> None:
        self.min_priority: Optional[Priority] = None
        self.priority_levels: list[PriorityLevel] = [list() for _ in range(priority_count)]
        self.priorities: defaultlist[Optional[Priority]] = defaultlist(lambda: None)
        self.indices: defaultlist[Optional[int]] = defaultlist(lambda: None)
        self.size: int = 0

    def minimums(self) -> Iterable[Priority]:
        assert self.min_priority is not None
        return self.priority_levels[self.min_priority]

    def __len__(self) -> int:
        return self.size

    def __contains__(self, key: Key) -> bool:
        assert key >= 0
        return self.priorities[key] is not None

    def get_priority(self, key: Key) -> Priority:
        assert key in self, f"Priority for {key} is {self.priorities[key]}"
        return self.priorities[key]

    def _remove_from_level(self, level: PriorityLevel, key: Key):
        index = self.indices[key]
        assert index is not None
        assert 0 <= index < len(level), f"Failed 0 <= {index} < {len(level)}"
        assert level[index] == key
        self.indices[key] = None

        if index == len(level) - 1:
            level.pop()
        else:
            move = level.pop()
            level[index] = move
            self.indices[move] = index

    def _add_to_level(self, level: PriorityLevel, key: Key) -> None:
        self.indices[key] = len(level)
        level.append(key)

    def _assert_priority(self, key: Key, priority: Priority) -> None:
        actual = self.get_priority(key)
        assert actual == priority, f"Expected priority {priority}, got {actual} instead"
        assert self.priority_levels[actual][self.indices[key]] == key

    def _remove_priority_entry(self, key: Key, priority: Priority) -> None:
        level = self.priority_levels[priority]
        self._remove_from_level(level, key)

    def _add_priority_entry(self, key: Key, priority: Priority) -> None:
        level = self.priority_levels[priority]
        self._add_to_level(level, key)

    def set_priority(self, key: Key, priority: Priority) -> None:
        assert priority < len(self.priority_levels)
        if self.min_priority is None or priority < self.min_priority:
            self.min_priority = priority

        is_already_present = key in self

        if is_already_present:
            old_priority = self.get_priority(key)
            if old_priority == priority:
                return
            self._remove_priority_entry(key, old_priority)
        else:
            self.size += 1

        self._add_priority_entry(key, priority)
        self.priorities[key] = priority

        self._adjust_min_priority()

        self._assert_priority(key, priority)
        assert len(self) > 0

    def increment(self, key: Key, delta: Priority, unset_on: Priority) -> None:
        new_priority = self.get_priority(key) + delta
        if new_priority == unset_on:
            self.unset_priority(key)
        else:
            self.set_priority(key, new_priority)

    def unset_priority(self, key: Key) -> None:
        assert key in self
        self.size -= 1
        priority = self.priorities[key]
        level = self.priority_levels[priority]
        self._remove_from_level(level, key)
        self.priorities[key] = None

        self._adjust_min_priority()

    def _adjust_min_priority(self) -> None:
        if len(self) == 0:
            self.min_priority = None
        else:
            while len(self.priority_levels[self.min_priority]) <= 0:
                self.min_priority += 1

    def __iter__(self) -> Iterator[Key]:
        count = 0

        for level in self.priority_levels:
            count += len(level)
            yield from level

        assert count == len(self)

    @partial(compose, list)
    def invariant_failures(self) -> Iterable[str]:
        """Returns a list of strings of which invariants do
        not hold on this instance"""

        for key in range(len(self.priorities)):
            priority = self.priorities[key]
            index = self.indices[key]

            if (priority is None) != (index is None):
                yield f"Priority and index are not in sync for {key}"
                continue

            if priority is None: continue
            if priority >= len(self.priority_levels):
                yield (f"Priority {priority} is "
                       f"too large for maximum "
                       f"{len(self.priority_levels)} (key: {key})")
                continue
            if index >= len(self.priority_levels[priority]):
                yield (f"Priority level {priority} "
                       f"is too short (key: {key})")
                continue

            if self.priority_levels[priority][index] != key:
                yield f"{self.priority_levels[priority][index]} does not match {key}"

    def test_invariants(self) -> None:
        failures = self.invariant_failures()
        if len(failures) == 0: return

        raise RuntimeError(f"Following {len(failures)} invariants where violated:\n"
                           f"{textwrap.indent("\n".join(failures), " " * 4)}\n"
                           f"Context:\n"
                           f"{self.size}\n"
                           f"{self.priorities}\n"
                           f"{self.indices}\n"
                           f"{self.priority_levels}")
