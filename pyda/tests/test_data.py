import datetime
from datetime import timezone
from unittest import mock

import pyds_model
import pytest

from pyda import data
from pyda.data import _data


@pytest.mark.parametrize(
    "ns,expected_datetime_args", [
        (1456698342000000000, (2016, 2, 28, 22, 25, 42, 0, timezone.utc)),
        (1456698342743902000, (2016, 2, 28, 22, 25, 42, 743902, timezone.utc)),
        (1391456625628407589, (2014, 2, 3, 19, 43, 45, 628408, timezone.utc)),
    ],
)
def test_datetime_from_ns(ns, expected_datetime_args):
    actual_time = _data.datetime_from_ns(ns)
    assert actual_time == datetime.datetime(*expected_datetime_args)


@pytest.mark.parametrize(
    "context,expected_conversion_arg", [
        (pyds_model.MultiplexedSettingContext('MULTIPLEXED.SETTINGS.CTX', 100, 200), 200),
        (pyds_model.SettingContext(100, 200), 200),
        (pyds_model.CycleBoundAcquisitionContext('CYCLEBOUND.ACQ.CTX', 100, 200), 200),
        (pyds_model.AcquisitionContext(100), 100),
    ],
)
@mock.patch('pyda.data._data.datetime_from_ns')
def test_header_acquisition_time(datetime_from_ns, context, expected_conversion_arg):
    header = data.Header(context)
    datetime_from_ns.assert_not_called()
    result = header.acquisition_time()
    datetime_from_ns.assert_called_once_with(expected_conversion_arg)
    assert result is datetime_from_ns.return_value


@pytest.mark.parametrize(
    "context,expected_conversion_arg", [
        (pyds_model.MultiplexedSettingContext('MULTIPLEXED.SETTINGS.CTX', 100), 100),
        (pyds_model.SettingContext(100), 100),
        (pyds_model.CycleBoundAcquisitionContext('CYCLEBOUND.ACQ.CTX', 100), None),
        (pyds_model.AcquisitionContext(), None),
    ],
)
@mock.patch('pyda.data._data.datetime_from_ns')
def test_header_set_time(datetime_from_ns, context, expected_conversion_arg):
    header = data.Header(context)
    datetime_from_ns.assert_not_called()
    result = header.set_time()
    if expected_conversion_arg is None:
        datetime_from_ns.assert_not_called()
        assert result is None
    else:
        datetime_from_ns.assert_called_once_with(expected_conversion_arg)
        assert result is datetime_from_ns.return_value


@pytest.mark.parametrize(
    "context,expected_conversion_arg", [
        (pyds_model.MultiplexedSettingContext('MULTIPLEXED.SETTINGS.CTX'), None),
        (pyds_model.SettingContext(), None),
        (pyds_model.CycleBoundAcquisitionContext('CYCLEBOUND.ACQ.CTX', 100), 100),
        (pyds_model.AcquisitionContext(), None),
    ],
)
@mock.patch('pyda.data._data.datetime_from_ns')
def test_header_cycle_time(datetime_from_ns, context, expected_conversion_arg):
    header = data.Header(context)
    datetime_from_ns.assert_not_called()
    result = header.cycle_time()
    if expected_conversion_arg is None:
        datetime_from_ns.assert_not_called()
        assert result is None
    else:
        datetime_from_ns.assert_called_once_with(expected_conversion_arg)
        assert result is datetime_from_ns.return_value


@pytest.mark.parametrize(
    "context,expected_sel", [
        (
                pyds_model.MultiplexedSettingContext('MULTIPLEXED.SETTINGS.CTX'),
                data.Selector('MULTIPLEXED.SETTINGS.CTX'),
        ),
        (pyds_model.SettingContext(), None),
        (
                pyds_model.CycleBoundAcquisitionContext('CYCLEBOUND.ACQ.CTX', 0),
                data.Selector('CYCLEBOUND.ACQ.CTX'),
        ),
        (pyds_model.AcquisitionContext(), None),
    ],
)
def test_header_selector(context, expected_sel):
    header = data.Header(context)
    assert header.selector == expected_sel


@pytest.mark.parametrize(
    "context,expected_stamp", [
        # We're not using default (0) value for the stamp argument,
        # because DSF will produce current time
        (pyds_model.MultiplexedSettingContext('MULTIPLEXED.SETTINGS.CTX', 0, 100), 100),
        (pyds_model.SettingContext(0, 100), 100),
        (pyds_model.CycleBoundAcquisitionContext('CYCLEBOUND.ACQ.CTX', 0, 200), 200),
        (pyds_model.AcquisitionContext(300), 300),
    ],
)
def test_header_acquisition_stamp(context, expected_stamp):
    header = data.Header(context)
    assert header.acquisition_timestamp == expected_stamp


@pytest.mark.parametrize(
    "context,expected_stamp", [
        (pyds_model.MultiplexedSettingContext('MULTIPLEXED.SETTINGS.CTX'), 0),
        (pyds_model.MultiplexedSettingContext('MULTIPLEXED.SETTINGS.CTX', 100), 100),
        (pyds_model.SettingContext(), 0),
        (pyds_model.SettingContext(100), 100),
        (pyds_model.CycleBoundAcquisitionContext('CYCLEBOUND.ACQ.CTX', 0), None),
        (pyds_model.CycleBoundAcquisitionContext('CYCLEBOUND.ACQ.CTX', 0, 200), None),
        (pyds_model.AcquisitionContext(), None),
        (pyds_model.AcquisitionContext(300), None),
    ],
)
def test_header_set_stamp(context, expected_stamp):
    header = data.Header(context)
    assert header.set_timestamp == expected_stamp


@pytest.mark.parametrize(
    "context,expected_stamp", [
        (pyds_model.MultiplexedSettingContext('MULTIPLEXED.SETTINGS.CTX'), None),
        (pyds_model.MultiplexedSettingContext('MULTIPLEXED.SETTINGS.CTX', 100), None),
        (pyds_model.SettingContext(), None),
        (pyds_model.SettingContext(100), None),
        (pyds_model.CycleBoundAcquisitionContext('CYCLEBOUND.ACQ.CTX', 0), 0),
        (pyds_model.CycleBoundAcquisitionContext('CYCLEBOUND.ACQ.CTX', 200), 200),
        (pyds_model.AcquisitionContext(), None),
        (pyds_model.AcquisitionContext(300), None),
    ],
)
def test_header_cycle_stamp(context, expected_stamp):
    header = data.Header(context)
    assert header.cycle_timestamp == expected_stamp


@pytest.mark.parametrize("value", ["TEST.USER.ALL", ""])
def test_Selector_str(value):
    sel = data.Selector(value)
    assert str(sel) == value


@pytest.mark.parametrize(
    "arg,expected_output", [
        ("TEST.USER.ALL", 'Selector("TEST.USER.ALL")'),
        ("", 'Selector("")'),
    ],
)
def test_Selector_repr(arg, expected_output):
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
def test_Selector_eq(obj1, obj2, expect_equal):
    assert (obj1 == obj2) == expect_equal
    assert (obj1 != obj2) != expect_equal


def test_response_init_fails():
    with pytest.raises(
        AssertionError, match='"value" and "exception" '
        'are mutually exclusive arguments',
    ):
        data.PropertyAccessResponse(
            query=mock.MagicMock(),
            value=mock.MagicMock(),
            exception=data.PropertyAccessError("Test error"),
        )


def test_response_value_succeeds():
    val = mock.MagicMock()
    resp = data.PropertyAccessResponse(
        query=mock.MagicMock(),
        value=val,
    )
    assert resp.value is val


def test_response_value_fails():
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
def test_response_str(kwargs, expected_str):
    resp = data.PropertyAccessResponse(**kwargs)
    assert str(resp) == expected_str
