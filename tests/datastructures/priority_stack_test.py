from hypothesis import given, strategies as st

from messthaler_wulff.datastructures.priority_stack import PriorityStack, PriorityMode

priority_count = 20
max_node = 20

action_strategy = st.lists(st.one_of(
    st.tuples(st.just("add"),
              st.integers(min_value=0, max_value=max_node),
              st.integers(min_value=0, max_value=priority_count - 1), ),
    st.tuples(st.just("remove"),
              st.integers(min_value=0, max_value=max_node),
              st.just(0)),
), max_size=1000)


def get_values(actions: list[tuple[str, int, int]], mode: PriorityMode):
    reference: dict[int, int] = {}
    p = PriorityStack(mode, priority_count)

    yield reference, p

    for a, node, key in actions:
        match a:
            case "add":
                p[node] = key
                reference[node] = key
                yield reference, p
            case "remove":
                if node not in reference: continue
                del p[node]
                del reference[node]
                yield reference, p


@given(action_strategy, st.one_of([st.just(x) for x in PriorityMode]))
def test_against_reference(actions: list[tuple[str, int, int]], mode: PriorityMode):
    for ref, p in get_values(actions, mode):
        for node, key in ref.items():
            assert p.priority_levels[key][p.indices[node]] == node

        assert frozenset(ref.keys()) == frozenset(p.select_levels(range(0, priority_count)))


@given(action_strategy, st.one_of([st.just(x) for x in PriorityMode]))
def test_extrema(actions: list[tuple[str, int, int]], mode: PriorityMode):
    for ref, p in get_values(actions, mode):
        extremum = p.extremal_key
        if extremum is None: return
        assert extremum == mode.function(ref.values())
        actual_extrema = frozenset([k for k, v in ref.items() if v == extremum])
        assert frozenset(p.extrema()) == actual_extrema


@given(action_strategy, st.one_of([st.just(x) for x in PriorityMode]))
def test_invariants(actions: list[tuple[str, int, int]], mode: PriorityMode):
    for _, p in get_values(actions, mode):
        p.test_invariants()
