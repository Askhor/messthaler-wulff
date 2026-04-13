import time
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps

_totals: defaultdict[str, float] = defaultdict(lambda: 0)
_counts: defaultdict[str, int] = defaultdict(lambda: 0)


@contextmanager
def measure(name: str, reset: bool = False):
    if reset:
        global _totals
        global _counts
        _totals = defaultdict(lambda: 0)
        _counts = defaultdict(lambda: 0)

    start = time.time_ns()
    yield None
    end = time.time_ns()

    _totals[name] += end - start
    _counts[name] += 1


def measure_function(function):
    @wraps(function)
    def impl(*args, **kwargs):
        with measure(function.__name__):
            return function(*args, **kwargs)

    return impl


def format_time(ns: int) -> str:
    units = ["ns", "μs", "ms", "s"]
    shrinker = 0

    while ns // (1000 ** shrinker) >= 1000 and shrinker < len(units) - 1:
        shrinker += 1

    return f"{ns // (1000 ** shrinker)} {units[shrinker]}"


def get_result(name: str) -> str:
    return f"{name}: {format_time(_totals[name] // _counts[name])} · {_counts[name]} = {format_time(_totals[name])}"


def all_results() -> str:
    return "; ".join(map(get_result, _totals.keys()))
