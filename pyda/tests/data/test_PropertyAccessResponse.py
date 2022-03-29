from unittest import mock

import pytest

from pyda import data


def test__PropertyRetrievalResponse__init__fails():
    with pytest.raises(
        AssertionError, match='"value" and "exception" '
        'are mutually exclusive arguments',
    ):
        data.PropertyRetrievalResponse(
            query=mock.MagicMock(),
            value=mock.MagicMock(),
            exception=data.PropertyAccessError("Test error"),
        )


def test__PropertyRetrievalResponse__value_succeeds():
    val = mock.MagicMock()
    resp = data.PropertyRetrievalResponse(
        query=mock.MagicMock(),
        value=val,
    )
    assert resp.value is val


def test__PropertyRetrievalResponse__value_fails():
    exc = data.PropertyAccessError("Test error")
    resp = data.PropertyRetrievalResponse(
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
                "-- PropertyRetrievalResponse from QUERY_OUTPUT --\n\n"
                "VALUE_OUTPUT",
        ),
        (
                {
                    "exception": data.PropertyAccessError("Test error"),
                    "query": "QUERY_OUTPUT",
                },
                "-- PropertyRetrievalResponse from QUERY_OUTPUT --\n\n"
                "Exception occurred: Test error",
        ),
    ],
)
def test__PropertyRetrievalResponse__str__(kwargs, expected_str):
    resp = data.PropertyRetrievalResponse(**kwargs)
    assert str(resp) == expected_str
