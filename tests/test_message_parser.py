import pytest
from parser_tests.data import msg_split, msg_join

from foghorn.message import Message


@pytest.mark.parametrize(
    "line, atoms",
    [
        pytest.param(test["input"], test["atoms"], id=test["input"])
        for test in msg_split["tests"]
    ],
)
def test_msg_split(line, atoms):
    msg = Message.from_line(line)
    assert msg.tags == atoms.get("tags")
    assert msg.source == atoms.get("source")
    assert msg.verb == atoms["verb"]
    assert msg.params == atoms.get("params", [])


@pytest.mark.parametrize(
    "atoms, line",
    [
        pytest.param(test["atoms"], test["matches"][0], id=test["desc"])
        for test in msg_join["tests"]
    ],
)
def test_msg_join(atoms, line):
    print(atoms)
    assert Message.from_line(line).to_line() == line
