import pytest
from parser_tests.data import mask_match, msg_join, msg_split

from foghorn.message import Message


@pytest.mark.parametrize(
    "line, atoms",
    [
        pytest.param(test["input"], test["atoms"], id=f"\"{test['input']}\"")
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
    "line",
    [
        pytest.param(test["matches"][0], id=f"\"{test['desc']}\"")
        for test in msg_join["tests"]
    ],
)
def test_msg_join(line):
    msg = Message.from_line(line)
    assert msg.to_line() == line


@pytest.mark.parametrize(
    "mask,matches,fails",
    [
        pytest.param(
            test["mask"], test["matches"], test["fails"], id=f"\"{test['mask']}\""
        )
        for test in mask_match["tests"]
    ],
)
def test_mask_expression_match(mask, matches, fails):
    candidates = matches + fails
    assert Message.match_expression(mask, candidates) == matches
