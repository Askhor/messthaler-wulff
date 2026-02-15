from hypothesis import given, strategies as st

from messthaler_wulff.priority_stack import PriorityStack

priority_count = 20
max_node = 20

action_strategy = st.lists(st.one_of(
    st.tuples(st.just("add"),
              st.integers(min_value=0, max_value=max_node),
              st.integers(min_value=0, max_value=priority_count - 1), ),
    st.tuples(st.just("remove"),
              st.integers(min_value=0, max_value=max_node),
              st.just(0)),
), max_size=100)


@given(action_strategy)
def test_against_reference(actions: list[tuple[str, int, int]]):
    reference: dict[int, int] = {}
    p = PriorityStack(priority_count)

    def reference_matches():
        for k, v in reference.items():
            assert p.get_priority(k) == v

        assert frozenset(reference.keys()) == frozenset(p)

    for a, arg1, arg2 in actions:
        match a:
            case "add":
                reference[arg1] = arg2
                p.set_priority(arg1, arg2)
                reference_matches()
            case "remove":
                if arg1 not in reference: continue
                del reference[arg1]
                p.unset_priority(arg1)
                reference_matches()


@given(action_strategy)
def test_minimums(actions: list[tuple[str, int, int]]):
    reference: dict[int, int] = {}
    p = PriorityStack(priority_count)

    def check_minimums():
        minimum = p.min_priority
        if minimum is None: return
        assert minimum == min(reference.values())
        actual_minimums = frozenset([k for k, v in reference.items() if v == minimum])
        assert frozenset(p.minimums()) == actual_minimums

    for a, arg1, arg2 in actions:
        match a:
            case "add":
                reference[arg1] = arg2
                p.set_priority(arg1, arg2)
                check_minimums()
            case "remove":
                if arg1 not in reference: continue
                del reference[arg1]
                p.unset_priority(arg1)
                check_minimums()


@given(action_strategy)
def test_invariants(actions: list[tuple[str, int, int]]):
    p = PriorityStack(priority_count)

    p.test_invariants()

    for a, arg1, arg2 in actions:
        match a:
            case "add":
                p.set_priority(arg1, arg2)
                p.test_invariants()
            case "remove":
                if arg1 in p:
                    p.unset_priority(arg1)
                p.test_invariants()
