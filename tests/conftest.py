import pytest


# a hacky way to get around our per-parsing Command validation. probably
# a better alternative to forcing string checking and recasting to the enum
# later during parsing
class DynamicEnumMock:
    def __init__(self):
        self.__members__ = DynamicEnumMock._Container()

    def __getitem__(self, key):
        return key

    class _Container:
        def __contains__(self, x):
            return True


@pytest.fixture
def mock_enum(monkeypatch):
    monkeypatch.setattr("foghorn.message.Command", DynamicEnumMock())
