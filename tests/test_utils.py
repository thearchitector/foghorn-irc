from foghorn.typing import typecaster


def test_typecaster():
    assert typecaster(int)(["foo"], iter(["0"])) == 0
    assert typecaster(str, optional=True)(["bar"], iter([])) is None
    assert typecaster(int, many=True)(["foo", "bar"], iter(["0", "42"])) == [0, 42]
