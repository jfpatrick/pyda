import functools
import logging
import typing

from ._core import BasePropertyStream

if typing.TYPE_CHECKING:
    from ..data import PropertyAccessResponse

SYNC_LOG = logging.getLogger(f'{__name__}.synchroniser')


class StreamChain(BasePropertyStream):
    """
    A non-leaf stage of stream processing.

    """
    def __init__(
            self,
            stream: BasePropertyStream,
            processor: typing.Callable[
                ["PropertyAccessResponse"],
                typing.Optional["PropertyAccessResponse"],
            ],
    ):
        self._processor = processor
        self._stream = stream
        super().__init__()

    def _response_received(self, response: "PropertyAccessResponse"):
        processed_resp = self._processor(response)
        if processed_resp is not None:
            self._broadcast_response(processed_resp)

    def start(self, subs):
        super().start(subs)
        self._stream.start(self)

    def stop(self, subs):
        super().stop(subs)
        self._stream.stop(self)


class StreamMiddleware:
    """
    A middleware is a mechanism to add additional processing before data
    arrives at a subscription.

    The essential method of a middleware is
    :meth:`wrap_stream``, which is the only opportunity of the middleware to
    insert the desired stream post-processing.

    """
    def wrap_stream(
            self,
            stream: BasePropertyStream,
    ) -> BasePropertyStream:
        # No-op middleware.
        return stream


class SynchronizerMiddleware(StreamMiddleware):
    def __init__(self):
        self._streams = []
        self._accumulations = {}
        # TODO: Handle thread-safety in this class.

    def wrap_stream(self, stream: BasePropertyStream) -> BasePropertyStream:
        wrapped_stream = StreamChain(
            stream,
            functools.partial(self.synchronised_response_handler, stream=stream),
        )
        self._streams.append(wrapped_stream)
        return wrapped_stream

    def synchronised_response_handler(
            self,
            response: "PropertyAccessResponse",
            *,
            stream: StreamChain,
    ) -> None:

        if not self._accumulations:
            # TODO: Start a timer which will raise if the accumulation does not
            #       complete in time.
            pass

        if id(stream) in self._accumulations:
            SYNC_LOG.info(
                f'Dropping existing data for {stream} before the accumulation is '
                f'complete, as newer data has arrived',
            )
        self._accumulations[id(stream)] = response

        if len(self._accumulations) == len(self._streams):
            SYNC_LOG.debug("Accumulation is complete")
            for stream in self._streams:
                resp = self._accumulations.pop(id(stream._stream))
                # Let the wrapped stream continue to process the data.
                stream._broadcast_response(resp)
        return None
