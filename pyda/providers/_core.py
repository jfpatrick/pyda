import concurrent.futures
import typing
import weakref

import typing_extensions

if typing.TYPE_CHECKING:
    from ..data import PropertyAccessQuery, PropertyAccessResponse


class StreamResponseHandlerProtocol(typing_extensions.Protocol):
    # Note that PropertyStream and client.Subscription are both stream handlers.
    def _response_received(self, response: "PropertyAccessResponse"):
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

    def _response_received(self, response: "PropertyAccessResponse") -> None:
        # Called by the provider sources when a response is received.
        self._broadcast_response(response)

    def _broadcast_response(self, response: "PropertyAccessResponse"):
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

    def _create_property_stream(self, query: "PropertyAccessQuery") -> BasePropertyStream:
        pass
