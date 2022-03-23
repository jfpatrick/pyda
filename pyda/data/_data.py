import dataclasses
import datetime
from datetime import timezone
import json
import typing


@dataclasses.dataclass(frozen=True)
class Header:
    acq_timestamp: typing.Optional[float] = None
    set_timestamp: typing.Optional[float] = None
    selector: str = ''

    def acq_time(self) -> typing.Optional[datetime.datetime]:
        return self._create_datetime(self.acq_timestamp)

    def set_time(self) -> typing.Optional[datetime.datetime]:
        return self._create_datetime(self.set_timestamp)

    def _create_datetime(
            self,
            timestamp: typing.Optional[float],
    ) -> typing.Optional[datetime.datetime]:
        if timestamp is None:
            return None
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
    selector: str
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
