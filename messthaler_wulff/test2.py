import itertools
import math
import operator
import sys
from collections import deque
from enum import Enum
from functools import singledispatchmethod, reduce
from typing import Iterator, Any, Self, cast, Callable, Optional, Iterable, Sequence

import networkx as nx
import tqdm
from networkx import is_weighted

from messthaler_wulff import myprofiler


def compose(a: Callable, b: Callable) -> Callable:
    def impl(*args, **kwargs):
        return a(b(*args, **kwargs))

    return impl


class ID:
    def __getitem__(self, x):
        return x


class HasAdd:
    def __add__(self, other):
        raise NotImplementedError(f"Cannot add {type(self)} to {type(other)}")

    def __radd__(self, other):
        return self + other


class HasMul:
    def __mul__(self, other):
        raise NotImplementedError(f"Cannot multiply {type(self)} with {type(other)}")

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return -1 * self


class HasAddNMul(HasAdd, HasMul):
    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other


# class PartialOrder[T](ABC):
#     def __le__(self, other: T) -> bool:
#         return other >= self
#
#     def __lt__(self, other: T) -> bool:
#         return self <= other and not self == other
#
#     def __gt__(self, other: T) -> bool:
#         return self >= other and not self == other
#
#     @abc.abstractmethod
#     def __ge__(self, other: T) -> bool:
#         ...
#
#     @abc.abstractmethod
#     def __eq__(self, other) -> bool:
#         ...


class IntervalSup: ...


class Interval(HasAddNMul, IntervalSup):
    def __init__(self, a: int, b: int) -> None:
        if b >= a:
            self.min: int = a
            self.max: int = b
        else:
            self.min = b
            self.max = a

    @singledispatchmethod
    def __add__(self, other):
        super().__add__(other)

    @__add__.register
    def _(self, other: int):
        return Interval(self.min + other, self.max + other)

    @__add__.register
    def _(self, other: IntervalSup):
        assert isinstance(other, Interval)

        return Interval(self.min + other.min, self.max + other.max)

    @singledispatchmethod
    def __mul__(self, other):
        super().__mul__(other)

    @__mul__.register
    def _(self, other: int):
        return Interval(self.min * other, self.max * other)

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return False

        return self.min == other.min and self.max == other.max

    @singledispatchmethod
    def __or__(self, other):
        raise NotImplementedError(f"Cannot union {type(self)} and {type(other)}")

    def __ror__(self, other):
        return self | other

    @__or__.register
    def _(self, other: IntervalSup):
        assert isinstance(other, Interval)
        return Interval(min(self.min, other.min), max(self.max, other.max))

    @__or__.register
    def _(self, other: int):
        return self | Interval(other, other)

    @singledispatchmethod
    @classmethod
    def cast(cls, value) -> Self:
        raise NotImplementedError(f"Cannot create an interval from {type(value)}")

    @cast.register
    @classmethod
    def _(cls, value: int):
        return cls(value, value)

    @cast.register
    @classmethod
    def _(cls, value: IntervalSup):
        assert isinstance(value, Interval)
        return value

    def range(self) -> range:
        return range(self.min, self.max + 1)

    def int(self) -> int:
        assert self.min == self.max
        return self.min

    def __str__(self):
        return f"{self.min}..{self.max}"

    @classmethod
    def from_values(cls, values) -> Self:
        return reduce(operator.or_, map(Interval.cast, values))


class SAFSup: ...


class SAF[T](HasAddNMul, SAFSup):
    def __init__(self, slf: dict[T, int], bias: int, mul: int = 1):
        assert mul != 0
        self.slf = slf
        self.bias = bias
        self.mul = mul

    def eval(self, values) -> Any:
        acc = Interval.cast(self.bias)

        for node, value in self.slf.items():
            with myprofiler.measure("Acc"):
                acc += self.mul * values(node) * value

        return acc

    def change_slf(self, slf_update: dict[T, int]) -> Self:
        new_slf = self.slf.copy()

        node: T
        value: int

        for node, value in slf_update.items():
            if value == 0:
                new_slf.pop(node, None)
            else:
                new_slf[node] = value

        return self.__class__(new_slf, self.bias, self.mul)

    @singledispatchmethod
    def __add__(self, other):
        super().__add__(other)

    @__add__.register
    def _(self, other: int) -> Self:
        return self.__class__(self.slf, self.bias + other, self.mul)

    @__add__.register
    def _(self, other: SAFSup) -> Self:
        assert isinstance(other, SAF)

        new_slf = {}

        for node, value in self.slf.items():
            new_slf[node] = self.mul * value

        for node, value in other.slf.items():
            if node in new_slf:
                new_slf[node] += other.mul * value
            else:
                new_slf[node] = other.mul * value

        return self.__class__(new_slf, self.bias + other.bias)

    @singledispatchmethod
    def __mul__(self, other):
        super().__mul__(other)

    @__mul__.register
    def _(self, other: int) -> Self:
        return self.__class__(self.slf, self.bias * other, self.mul * other)

    def __str__(self):
        return f"{self.mul}*{self.slf}+{self.bias}"

    def __repr__(self):
        return str(self)


type Candidate = tuple[frozenset[Any], SAF[Any]]
type NodeCount = int


def candidate_without_node(graph: nx.Graph, candy: Candidate, node: Any) -> Candidate:
    nodes, saf = candy
    return nodes, saf.change_slf({node: 0})


def candidate_with_node(graph: nx.Graph, nodes_processed: set[Any], candy: Candidate, node: Any) -> Candidate:
    values, saf = candy
    energy_delta = graph.nodes[node]["weight"]
    slf_changes = {node: 0}

    for neighbor in graph.neighbors(node):
        edge_weight = graph.edges[node, neighbor]["weight"]
        if neighbor in values:
            energy_delta += 2 * edge_weight
        elif neighbor not in nodes_processed:
            slf_changes[neighbor] = edge_weight

    return values | frozenset([node]), saf.change_slf(slf_changes) + energy_delta


def check_graph_validity(graph: nx.Graph):
    error = False

    if graph.is_directed():
        print("The graph is directed")
        error = True

    if not is_weighted(graph):
        print("Not all edges in the graph have weights")
        error = True

    for a, data in graph.nodes(data=True):
        if "weight" not in data:
            print(f"The node {a} in the graph was not assigned a weight")
            error = True

    for a, b in graph.edges:
        if graph.edges[a, b]["weight"] != graph.edges[b, a]["weight"]:
            print(f"The edge ({a}, {b}) has a different weight to ({b}, {a})")
            error = True

    if error:
        sys.exit(-1)


def generate_candidates_leaving_out(graph: nx.Graph, candidates: list[Candidate], node: Any):
    for candy in candidates:
        yield candidate_without_node(graph, candy, node)


def generate_candidates_adding(graph: nx.Graph, nodes_processed: set[Any], candidates: list[Candidate], node: Any):
    for candy in candidates:
        new_candy = candidate_with_node(graph, nodes_processed, candy, node)
        assert len(new_candy[0]) == len(candy[0]) + 1
        yield new_candy


def visualise_candidate(candy: Candidate, bounds_x=None, bounds_y=None):
    values, saf = candy
    if len(values) == 0:
        print("empty")
        return

    assert all(len(v) == 2 for v in values)

    if bounds_x is None:
        bounds_x = Interval.from_values(map(lambda t: t[0], values))
    if bounds_y is None:
        bounds_y = Interval.from_values(map(lambda t: t[1], values))

    for y in bounds_y.range():
        print(end="|")
        for x in bounds_x.range():
            char = "X" if (x, y) in values else " "
            print(end=char)
        print("|")


class MyList[T]:
    def __init__(self, offset: int, _list: Optional[Iterable[T]] = None):
        self._offset: int = offset
        if _list is None:
            self._list: list[T] = []
        else:
            self._list = list(_list)

    def append(self, index: int, element: T):
        internal_index = index - self._offset
        assert internal_index == len(self._list)
        self._list.append(element)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index: int) -> T:
        if not self._offset <= index < self._offset + len(self._list):
            raise IndexError(f"Index {index} not in {self._offset}..{self._offset + len(self._list) - 1}")

        internal_index = index - self._offset
        return self._list[internal_index]

    def __iter__(self):
        return iter(self._list)

    @property
    def last(self) -> T:
        return self._list[-1]


class CandidateTracker:
    def __init__(self):
        self._zero_candy: Candidate = (frozenset(), SAF({}, 0, 1))
        self._zero_list = [self._zero_candy]
        self._empty_list = []
        self._candidates: MyList[MyList[list[Candidate]]] = MyList(1)

    def add_node_count(self, node_count: NodeCount):
        self._candidates.append(node_count, MyList(node_count))

    def set_candidates(self, node_count: NodeCount, node_index: int, new_candidates: list[Candidate]):
        if node_count == 0 or node_index < node_count:
            raise IndexError("node_count or ra_index invalid")

        self._candidates[node_count].append(node_index, new_candidates)

    def get_candidates(self, node_count: NodeCount, node_index: int) -> list[Candidate]:
        if node_count == 0: return self._zero_list
        if node_index < node_count: return self._empty_list
        return self._candidates[node_count][node_index]

    def get_final_candidates(self, node_count: NodeCount) -> list[Candidate]:
        return self._candidates[node_count].last

    def print(self):
        for lst in self._candidates:
            print(end=" " * 4 * lst._offset)
            print(*lst, sep=", ")


def optimise(graph: nx.Graph, discarding_strategy) -> Iterator[int]:
    check_graph_validity(graph)

    yield 0

    nodes_ordered = MyList(1, bfs(graph, next(iter(graph))))
    candidates = CandidateTracker()

    node_count: NodeCount
    for node_count in itertools.count(1):
        if node_count > len(graph):
            break

        candidates.add_node_count(node_count)
        nodes_processed = set()

        pbar = tqdm.tqdm(range(node_count, len(nodes_ordered) + 1))
        for node_index in pbar:
            with myprofiler.measure("Main", reset=True):
                node = nodes_ordered[node_index]
                nodes_processed.add(node)
                raw_a = candidates.get_candidates(node_count, node_index - 1)
                raw_b = candidates.get_candidates(node_count - 1, node_index - 1)
                assert len(raw_a) + len(raw_b) > 0
                with myprofiler.measure("Generating"):
                    input_a = list(generate_candidates_leaving_out(graph, raw_a, node))
                    input_b = list(generate_candidates_adding(graph, nodes_processed, raw_b, node))

                with myprofiler.measure("Discarding"):
                    new_candidates = discarding_strategy(itertools.chain(input_a, input_b))

                assert len(new_candidates) > 0, (f"Got no new candidates at {node_count=} and {node_index=}, "
                                                 f"the raw input was {len(raw_a)} + {len(raw_b)} candidates")

                # TODO
                # print("-----")
                # for candy in new_candidates:
                #     visualise_candidate(candy, Interval(0, 2), Interval(0, 2))
                #     print(candy[1])

                candidates.set_candidates(node_count, node_index, new_candidates)

                assert all(len(values) == node_count for values, saf in
                           new_candidates), f"{node_count=}, {new_candidates=}, {candidates.print()}"

            pbar.set_description(f"Nr. candidates: {len(new_candidates)}; {myprofiler.all_results()}")

        assert len(candidates.get_final_candidates(node_count)) >= 1
        yield min(saf.eval(lambda n: 0).int() for values, saf in candidates.get_final_candidates(node_count))


    return impl


def eval_candy(x: SAF) -> Interval:
    return cast(Interval, x.eval(lambda n: Interval(0, 1)))


def STRATEGY_BRUTE_FORCE(candidates: Iterator[Candidate]) -> list[Candidate]:
    return list(candidates)


@myprofiler.measure_function
def STRATEGY_ELIMINATE_WORST(candidates: Iterator[Candidate]) -> list[Candidate]:
    candidates_list = list(candidates)
    assert len(candidates_list) > 0

    best: Candidate = candidates_list[0]
    smallest_max = eval_candy(best[1]).max

    for i in range(1, len(candidates_list)):
        cur_max = eval_candy(candidates_list[i][1]).max
        if cur_max < smallest_max:
            smallest_max = cur_max
            best = candidates_list[i]

    result = [candy for candy in candidates_list if eval_candy(candy[1]).min < smallest_max]
    if len(result) == 0:
        result = [best]

    assert len(result) > 0
    return result


def list_unordered_remove[T](_list: list[T], index: int) -> None:
    if not 0 <= index < len(_list):
        raise IndexError(f"Index {index} not in 0..{len(_list) - 1}")

    if index == len(_list) - 1:
        _list.pop()
    else:
        last = _list.pop()
        _list[index] = last


@myprofiler.measure_function
def STRATEGY_SLOW_ELIMINATION(candidates: Iterator[Candidate]) -> list[Candidate]:
    good_candidates: list[Candidate] = []
    candy_count = 0

    for candy in candidates:
        candy_count += 1
        vals, saf = candy

        is_good = True

        for i in range(len(good_candidates) - 1, -1, -1):
            good_saf = good_candidates[i][1]

            with myprofiler.measure("Calculating Difference"):
                diff = saf - good_saf

            with myprofiler.measure("Evaluating Difference"):
                res = eval_candy(diff)

            if not res.min < 0:
                is_good = False
                break
            if not res.max > 0:
                list_unordered_remove(good_candidates, i)

        if is_good:
            good_candidates.append(candy)

        assert len(good_candidates) > 0

    assert len(good_candidates) > 0, f"{candy_count=}"

    return good_candidates


def STRATEGY_TEST(a, b, candidates: Iterator[Candidate]) -> list[Candidate]:
    candidates = list(candidates)

    result_a = a(candidates)
    result_b = b(candidates)
    set_a = set(result_a)
    set_b = set(result_b)

    assert set_a == set_b, f"{set_a - set_b} {set_b - set_a}\n{candidates}\n{result_a}\n{result_b}"

    return result_a


def STRATEGY_TEST_INTERSECTION_EFFICACY(candidates: Iterator[Candidate]) -> list[Candidate]:
    candidates: list[Candidate] = list(candidates)
    intersections = 0

    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            if len(candidates[i][1].slf.keys() & candidates[j][1].slf.keys()) > 0:
                intersections += 1

    if intersections > 1000:
        print(f"{intersections=} {len(candidates)=} {intersections / ((len(candidates) ** 2) / 2):.2%}")

    return candidates


def bfs(graph: nx.Graph, root) -> Iterator:
    queue = deque([root])
    visited = set()

    while len(queue) > 0:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)

        yield node

        for n in graph.neighbors(node):
            queue.append(n)


type Vector = Sequence[int]


class UniformNeighborhood:
    """A neighborhood of nodes in a graph that has the same degree and structure at every point"""

    def __init__(self, neighbors: list[Vector]) -> None:
        self.dimension = len(neighbors[0])
        assert all(len(v) == self.dimension for v in neighbors)
        self._neighbors = neighbors
        self.degree = len(self._neighbors)
        self.zero = tuple([0] * self.dimension)

    def neighbor(self, node: Vector, index: int) -> Vector:
        neighbor = self._neighbors[index]
        assert len(node) == len(neighbor), f"Dimension mismatch between {node} and {neighbor}"

        return tuple(node[i] + neighbor[i] for i in range(len(node)))

    @classmethod
    def from_basis(cls, basis: list[Vector]) -> Self:
        """This function inserts the inverses of the basis vectors"""
        return cls([*basis, *(tuple(map(lambda x: -x, v)) for v in basis)])

    def graph(self, radius: int) -> nx.Graph:
        g = nx.Graph()
        g.add_node(self.zero, weight=self.degree, radius=0)

        queue = deque([self.zero])
        visited = set()

        while len(queue) > 0:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            r = g.nodes[node]["radius"]

            if r >= radius: continue

            for i in range(self.degree):
                n = self.neighbor(node, i)
                g.add_node(n, weight=self.degree, radius=r + 1)
                g.add_edge(node, n, weight=-1)
                queue.append(n)

        return g


class CommonLattice(Enum):
    square = UniformNeighborhood.from_basis([
        [1, 0],
        [0, 1]])

    cubic = UniformNeighborhood.from_basis([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]])

    triangular = UniformNeighborhood.from_basis([
        [1, 0],
        [1, 1],
        [0, 1]])

    fcc = UniformNeighborhood.from_basis([
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (-1, 0, 1), (1, -1, 0), (0, 1, -1)])


def main() -> None:
    atoms = 400
    sl = 2 * int(math.sqrt(atoms))
    graph: nx.Graph = CommonLattice.fcc.value.graph(sl)
    print(f"The graph has {len(graph)} nodes")

    strategy = compose(STRATEGY_SLOW_ELIMINATION, STRATEGY_ELIMINATE_WORST)

    for node_count, energy in enumerate(optimise(graph, strategy)):
        print(f"{node_count=} {energy=}")
        if node_count >= atoms: break


if __name__ == "__main__":
    main()
