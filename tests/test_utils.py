from foghorn.utils import typecaster


def test_typecaster():
    assert typecaster(int)("0") == 0
    assert typecaster(int)(None) is None
    assert typecaster(str)("0") == "0"
