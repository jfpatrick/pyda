import concurrent.futures
import typing
import weakref

from pyds_model._ds_model import AnyData  # noqa
import typing_extensions

from ..data._data import anydata_from_dict

if typing.TYPE_CHECKING:
    from ..data import PropertyAccessQuery, PropertyRetrievalResponse


class StreamResponseHandlerProtocol(typing_extensions.Protocol):
    # Note that PropertyStream and client.Subscription are both stream handlers.
    def _response_received(self, response: "PropertyRetrievalResponse"):
        pass


class BasePropertyStream:
    # Represents a source of device property data which is continuous.
    # This is the basis of data for subscriptions.

    def __init__(self):
        #: A set of stream handlers (e.g. client subscriptions) (weakrefs)
        #: which will be called (with only the response) each time data arrives.
        self._stream_handlers = weakref.WeakSet()

    def _register_stream_handler(self, subs):
        self._stream_handlers.add(subs)

    def _response_received(self, response: "PropertyRetrievalResponse") -> None:
        # Called by the provider sources when a response is received.
        self._broadcast_response(response)

    def _broadcast_response(self, response: "PropertyRetrievalResponse"):
        for stream_handler in self._stream_handlers:
            stream_handler._response_received(response)

    def start(self, stream_handler: StreamResponseHandlerProtocol):
        self._register_stream_handler(stream_handler)

    def stop(self, stream_handler: StreamResponseHandlerProtocol):
        """
        **Note!**: Stop is not guaranteed to be called upon destruction.
        """
        self._stream_handlers.remove(stream_handler)


class BaseProvider:
    def _get_property(self, query: "PropertyAccessQuery") -> concurrent.futures.Future:
        pass

    def _set_property(
            self,
            query: "PropertyAccessQuery",
            value: typing.Any,
    ) -> concurrent.futures.Future:
        pass

    def _prepare_value_for_set(
            self,
            query: "PropertyAccessQuery",
            value: typing.Any,
    ) -> AnyData:
        # TODO: This would become a DeviceProperty behaviour if we have such a type in the future.

        if not isinstance(value, (AnyData, dict)):
            raise TypeError(f"Value must be either DataTypeValue or dict. Got {type(value)}")

        if isinstance(value, dict):
            # We don't use the query in this base implementation, but it is useful if context
            # specific conversions are needed (as is done in PyJapc).
            _ = query
            value = anydata_from_dict(value)

        return value

    def _create_property_stream(self, query: "PropertyAccessQuery") -> BasePropertyStream:
        pass
