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
def test__datetime_from_ns(ns, expected_datetime_args):
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
def test__Header__acquisition_time(datetime_from_ns, context, expected_conversion_arg):
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
def test__Header__set_time(datetime_from_ns, context, expected_conversion_arg):
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
def test__Header__cycle_time(datetime_from_ns, context, expected_conversion_arg):
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
def test__Header__selector(context, expected_sel):
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
def test__Header__acquisition_timestamp(context, expected_stamp):
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
def test__Header__set_timestamp(context, expected_stamp):
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
def test__Header__cycle_timestamp(context, expected_stamp):
    header = data.Header(context)
    assert header.cycle_timestamp == expected_stamp


@pytest.mark.parametrize(
    "context,expected_str", [
        (
                pyds_model.MultiplexedSettingContext(
                    'MULTIPLEXED.SETTINGS.CTX',
                    set_stamp=int(10e9),
                    acquisition_stamp=int(20e9),
                ),
                '[selector=MULTIPLEXED.SETTINGS.CTX, acquisition_time=1970-01-01 '
                '00:00:20+00:00, set_time=1970-01-01 00:00:10+00:00]',
        ),
        (
                pyds_model.SettingContext(
                    set_stamp=int(10e9),
                    acquisition_stamp=int(20e9),
                ),
                '[acquisition_time=1970-01-01 '
                '00:00:20+00:00, set_time=1970-01-01 00:00:10+00:00]',
        ),
        (
                pyds_model.CycleBoundAcquisitionContext(
                    'CYCLEBOUND.ACQ.CTX',
                    cycle_stamp=int(30e9),
                    acquisition_stamp=int(20e9),
                ),
                '[selector=CYCLEBOUND.ACQ.CTX, acquisition_time=1970-01-01 '
                '00:00:20+00:00, cycle_time=1970-01-01 00:00:30+00:00]',
        ),
        (
                pyds_model.AcquisitionContext(acquisition_stamp=int(20e9)),
                '[acquisition_time=1970-01-01 00:00:20+00:00]',
        ),
    ],
)
def test__Header__str__(context, expected_str):
    header = data.Header(context)
    assert str(header) == expected_str
