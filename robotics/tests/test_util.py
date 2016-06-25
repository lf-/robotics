from .. import util


def test_translate():
    assert util.translate(0, -1, 1, 0, 10) == 5
