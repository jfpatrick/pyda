import pytest

from pyda import data


@pytest.mark.parametrize("value", ["TEST.USER.ALL", ""])
def test__Selector__str__(value):
    sel = data.Selector(value)
    assert str(sel) == value


@pytest.mark.parametrize(
    "arg,expected_output", [
        ("TEST.USER.ALL", 'Selector("TEST.USER.ALL")'),
        ("", 'Selector("")'),
    ],
)
def test__Selector__repr__(arg, expected_output):
    sel = data.Selector(arg)
    assert repr(sel) == expected_output


@pytest.mark.parametrize(
    "obj1,obj2,expect_equal", [
        (
            data.Selector("DOM1.GR1.VAL1"),
            None,
            False,
        ),
        (
            data.Selector("DOM1.GR1.VAL1"),
            "DOM1.GR1.VAL1",
            False,
        ),
        (
            data.Selector("DOM1.GR1.VAL1"),
            data.Selector("DOM2.GR1.VAL1"),
            False,
        ),
        (
            data.Selector("DOM1.GR1.VAL1"),
            data.Selector("DOM1.GR1.VAL1"),
            True,
        ),
        (
            data.Selector(""),
            "",
            False,
        ),
        (
            data.Selector(""),
            data.Selector(""),
            True,
        ),
    ],
)
def test__Selector__eq__(obj1, obj2, expect_equal):
    assert (obj1 == obj2) == expect_equal
    assert (obj1 != obj2) != expect_equal
