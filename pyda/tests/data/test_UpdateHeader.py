import pytest

from pyda import data


@pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
def test__UpdateHeader__selector(selector):
    header = data.UpdateHeader(selector=data.Selector(selector))
    assert header.selector == data.Selector(selector)


@pytest.mark.parametrize(
    "selector,expected_str", [
        ("", '[selector=]'),
        ("TEST.USER.ALL", '[selector=TEST.USER.ALL]'),
    ],
)
def test__Header__str__(selector, expected_str):
    header = data.UpdateHeader(selector)
    assert str(header) == expected_str
