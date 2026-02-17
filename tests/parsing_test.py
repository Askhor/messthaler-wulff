from hypothesis import given, strategies as st

from messthaler_wulff.parsing import parse_crystal, crystal_re, allowed_characters


@given(st.lists(st.lists(st.integers(), min_size=1).map(tuple)))
def test_random_lists(l: list[tuple]):
    assert parse_crystal(str(l)) == l


@given(st.from_regex(crystal_re, fullmatch=True))
def test_random_data(string: str):
    result = parse_crystal(string)
    assert isinstance(result, list)

@given(st.lists(st.lists(st.integers(), min_size=1).map(tuple)))
def test_allowed_characters(l: list[tuple]):
    assert frozenset(str(l)) < allowed_characters
