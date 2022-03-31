from unittest import mock

import pytest

from pyda import data


def test__PropertyUpdateResponse__init__fails():
    with pytest.raises(
        AssertionError, match='"header" and "exception" '
        'are mutually exclusive arguments',
    ):
        data.PropertyUpdateResponse(
            query=mock.MagicMock(),
            header=mock.MagicMock(),
            exception=data.PropertyAccessError("Test error"),
        )


def test__PropertyUpdateResponse__header_succeeds():
    header = mock.MagicMock()
    resp = data.PropertyUpdateResponse(
        query=mock.MagicMock(),
        header=header,
    )
    assert resp.header is header


def test__PropertyUpdateResponse__header_fails():
    exc = data.PropertyAccessError("Test error")
    resp = data.PropertyUpdateResponse(
        query=mock.MagicMock(),
        exception=exc,
    )
    assert resp.exception is exc
    with pytest.raises(data.PropertyAccessError, match="Test error"):
        resp.header


@pytest.mark.parametrize(
    "kwargs,expected_str", [
        (
                {"header": "HEADER_OUTPUT", "query": "QUERY_OUTPUT"},
                "-- PropertyUpdateResponse from QUERY_OUTPUT --\n\n"
                "HEADER_OUTPUT",
        ),
        (
                {
                    "exception": data.PropertyAccessError("Test error"),
                    "query": "QUERY_OUTPUT",
                },
                "-- PropertyUpdateResponse from QUERY_OUTPUT --\n\n"
                "Exception occurred: Test error",
        ),
    ],
)
def test__PropertyUpdateResponse__str__(kwargs, expected_str):
    resp = data.PropertyUpdateResponse(**kwargs)
    assert str(resp) == expected_str
