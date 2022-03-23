import datetime
from datetime import timezone

import pytest

from pyda import data


@pytest.mark.parametrize(
    "ns,expected_datetime_args", [
        (1456698342000000000, (2016, 2, 28, 22, 25, 42, 0, timezone.utc)),
        (1456698342743902000, (2016, 2, 28, 22, 25, 42, 743902, timezone.utc)),
        (1391456625628407589, (2014, 2, 3, 19, 43, 45, 628408, timezone.utc)),
    ],
)
def test_header_acq_time(ns, expected_datetime_args):
    header = data.Header(acq_timestamp=ns)
    acq_time = header.acq_time()
    assert acq_time == datetime.datetime(*expected_datetime_args)


@pytest.mark.parametrize(
    "ns,expected_datetime_args", [
        (1456698342000000000, (2016, 2, 28, 22, 25, 42, 0, timezone.utc)),
        (1456698342743902000, (2016, 2, 28, 22, 25, 42, 743902, timezone.utc)),
        (1391456625628407589, (2014, 2, 3, 19, 43, 45, 628408, timezone.utc)),
    ],
)
def test_header_set_time(ns, expected_datetime_args):
    header = data.Header(set_timestamp=ns)
    set_time = header.set_time()
    assert set_time == datetime.datetime(*expected_datetime_args)
