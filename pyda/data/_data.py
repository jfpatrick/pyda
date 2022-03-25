import dataclasses
import datetime
from datetime import timezone
import json
import typing

import pyds_model


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


@dataclasses.dataclass(frozen=True)
class AcquiredPropertyData:
    # Known as AcquiredParameterValue in UCAP
    header: Header

    def __getitem__(self, item):
        return 'some-value'


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


class PropertyAccessResponse:
    # Known as FailSafeParameterValue in UCAP

    def __init__(
            self,
            query: PropertyAccessQuery,
            value: typing.Optional[AcquiredPropertyData] = None,
            exception: typing.Optional[PropertyAccessError] = None,
    ):
        super().__init__()
        self._value = value
        self._exception = exception
        self._query = query
        assert value or exception

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

    def __str__(self):
        val = f"-- {self.__class__.__qualname__} from {self.query} --\n\n"
        try:
            val += str(self.value)
        except PropertyAccessError as e:
            val += f"Exception occurred: {e}"
        return val

    def __repr__(self):
        val = self.__class__.__qualname__ + f'(query="{self.query}", '
        try:
            val += f"value={self.value}"
        except PropertyAccessError as e:
            val += f"exception={repr(e)}"
        val += ")"
        return val
