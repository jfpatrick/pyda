import dataclasses
import datetime
from datetime import timezone
import json
import typing

import numpy as np
import pyds_model
from pyds_model._ds_model import AnyData  # noqa


class Selector:

    def __init__(self, value: str):
        self._value = value

    def __bool__(self):
        return bool(self._value)

    def __eq__(self, other):
        return type(self) is type(other) and str(self) == str(other)

    def __str__(self):
        return self._value

    def __repr__(self):
        return f'{self.__class__.__qualname__}("{self._value}")'


class Header:

    def __init__(self, context: pyds_model.AnyContext):
        super().__init__()
        self._context = context

    @property
    def selector(self) -> typing.Optional[Selector]:
        selector = getattr(self._context, 'selector', None)
        if isinstance(selector, str):
            return Selector(selector)
        return selector

    @property
    def acquisition_timestamp(self) -> float:
        return self._context.acquisition_stamp

    def acquisition_time(self) -> datetime.datetime:
        return datetime_from_ns(self.acquisition_timestamp)

    @property
    def set_timestamp(self) -> typing.Optional[float]:
        return getattr(self._context, 'set_stamp', None)

    def set_time(self) -> typing.Optional[datetime.datetime]:
        timestamp = self.set_timestamp
        return (
            datetime_from_ns(timestamp)
            if timestamp is not None else None
        )

    @property
    def cycle_timestamp(self) -> typing.Optional[float]:
        return getattr(self._context, 'cycle_stamp', None)

    def cycle_time(self) -> typing.Optional[datetime.datetime]:
        timestamp = self.cycle_timestamp
        return (
            datetime_from_ns(timestamp)
            if timestamp is not None else None
        )


def datetime_from_ns(timestamp: float) -> datetime.datetime:
    sec = timestamp / 1e9
    us = round((timestamp / 1e3) % 1e6)
    dt = datetime.datetime.fromtimestamp(sec, tz=timezone.utc)
    dt = dt.replace(microsecond=us)
    return dt


class AcquiredPropertyData:
    # Known as AcquiredParameterValue in UCAP

    def __init__(self, dtv: pyds_model.DataTypeValue, header: Header):
        # TODO: Ensure we proxy all of the appropriate methods from DTV.
        self._dtv = dtv
        self._header = header

    def __getitem__(self, key):
        # TODO: If a numpy type, make it read-only.
        return self._dtv[key]

    def __contains__(self, key):
        return key in self._dtv

    def get(self, key: str, default: typing.Optional[typing.Any] = None):
        return self._dtv.get(key, default)

    def keys(self) -> typing.Iterable[typing.Any]:
        return self._dtv.keys()

    def values(self) -> typing.Iterable[typing.Any]:
        return self._dtv.values()

    def items(self) -> typing.Iterable[typing.Tuple[typing.Any, typing.Any]]:
        return self._dtv.items()

    @property
    def header(self) -> Header:
        return self._header

    @property
    def data_type(self) -> pyds_model.DataType:
        # TODO: This should be immutable.
        return self._dtv.data_type

    def mutable_data(self) -> typing.Dict[str, typing.Any]:
        return {k: v for k, v in self.items()}


class PropertyAccessError(Exception):
    # Known as ParameterException in UCAP
    # This is a placeholder for any relevant meta-information
    # (e.g. Header information, and exception_time)
    pass


@dataclasses.dataclass(frozen=True)
class PropertyAccessQuery:
    device: str
    prop: str
    selector: Selector
    data_filters: typing.Mapping[str, typing.Any] = dataclasses.field(default_factory=dict)

    def __str__(self):
        val = f'"{self.device}/{self.prop}"'
        if self.selector:
            val += f' @ "{self.selector}"'
        if self.data_filters:
            val += f' [DATA FILTERS: {json.dumps(self.data_filters)}]'
        return val


class PropertyRetrievalResponse:
    # Known as FailSafeParameterValue in UCAP

    def __init__(
            self,
            query: PropertyAccessQuery,
            notification_type: typing.Optional[str] = None,
            value: typing.Optional[AcquiredPropertyData] = None,
            exception: typing.Optional[PropertyAccessError] = None,
    ):
        super().__init__()
        self._value = value
        self._exception = exception
        self._query = query
        self._notification_type = notification_type
        assert (value is None) != (exception is None), \
            '"value" and "exception" are mutually exclusive arguments'

    @property
    def value(self) -> AcquiredPropertyData:
        if self._exception:
            raise self._exception
        assert self._value is not None
        return self._value

    @property
    def exception(self) -> typing.Optional[PropertyAccessError]:
        return self._exception

    @property
    def query(self) -> PropertyAccessQuery:
        return self._query

    @property
    def notification_type(self) -> typing.Optional[str]:
        return self._notification_type

    def __str__(self):
        val = f"-- {self.__class__.__qualname__} from {self.query} --\n\n"
        try:
            val += str(self.value)
        except PropertyAccessError as e:
            val += f"Exception occurred: {e}"
        return val


class UpdateHeader:

    def __init__(self, selector: Selector):
        super().__init__()
        self._selector = selector

    @property
    def selector(self) -> Selector:
        return self._selector


class PropertyUpdateResponse:
    # Known as FailSafeParameterValue in UCAP

    def __init__(
            self,
            query: PropertyAccessQuery,
            header: typing.Optional[UpdateHeader] = None,
            exception: typing.Optional[PropertyAccessError] = None,
    ):
        super().__init__()
        self._header = header
        self._exception = exception
        self._query = query
        assert (header is None) != (exception is None), \
            '"header" and "exception" are mutually exclusive arguments'

    @property
    def header(self) -> UpdateHeader:
        if self._exception:
            raise self._exception
        assert self._header is not None
        return self._header

    @property
    def exception(self) -> typing.Optional[PropertyAccessError]:
        return self._exception

    @property
    def query(self) -> PropertyAccessQuery:
        return self._query

    def __str__(self):
        val = f"-- {self.__class__.__qualname__} from {self.query} --\n\n"
        try:
            val += str(self.header)
        except PropertyAccessError as e:
            val += f"Exception occurred: {e}"
        return val


def anydata_from_dict(value: typing.Dict) -> AnyData:
    """
    Convert a dictionary into an AnyData using numpy type casting rules.

    """
    # TODO: We will want to extend this transformation on a per-provider basis
    #       when we have additional property metadata (including type info) as
    #       this will allow us to make more informed decisions when converting
    #       to numpy types.
    dtv: AnyData = AnyData.create()

    for k, v in value.items():
        vs = np.array(v)
        if vs.ndim == 0:
            # Take the scalar out of a 0-d array. Note that .item() will extract Python
            # types, whereas we want to preserve numpy types (scalars).
            vs = vs[()]
        dtv[k] = vs
    return dtv
