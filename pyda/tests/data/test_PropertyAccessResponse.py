from unittest import mock

import pytest

from pyda import data


def test__PropertyAccessResponse__init__fails():
    with pytest.raises(
        AssertionError, match='"value" and "exception" '
        'are mutually exclusive arguments',
    ):
        data.PropertyAccessResponse(
            query=mock.MagicMock(),
            value=mock.MagicMock(),
            exception=data.PropertyAccessError("Test error"),
        )


def test__PropertyAccessResponse__value_succeeds():
    val = mock.MagicMock()
    resp = data.PropertyAccessResponse(
        query=mock.MagicMock(),
        value=val,
    )
    assert resp.value is val


def test__PropertyAccessResponse__value_fails():
    exc = data.PropertyAccessError("Test error")
    resp = data.PropertyAccessResponse(
        query=mock.MagicMock(),
        exception=exc,
    )
    assert resp.exception is exc
    with pytest.raises(data.PropertyAccessError, match="Test error"):
        resp.value


@pytest.mark.parametrize(
    "kwargs,expected_str", [
        (
                {"value": "VALUE_OUTPUT", "query": "QUERY_OUTPUT"},
                "-- PropertyAccessResponse from QUERY_OUTPUT --\n\n"
                "VALUE_OUTPUT",
        ),
        (
                {
                    "exception": data.PropertyAccessError("Test error"),
                    "query": "QUERY_OUTPUT",
                },
                "-- PropertyAccessResponse from QUERY_OUTPUT --\n\n"
                "Exception occurred: Test error",
        ),
    ],
)
def test__PropertyAccessResponse__str__(kwargs, expected_str):
    resp = data.PropertyAccessResponse(**kwargs)
    assert str(resp) == expected_str
