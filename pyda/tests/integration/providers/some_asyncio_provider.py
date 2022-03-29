import asyncio
import concurrent.futures
import threading
import typing

from pyda.providers._core import BasePropertyStream, BaseProvider

if typing.TYPE_CHECKING:
    from pyda.data import PropertyAccessQuery


class AsyncIOPropertyStream(BasePropertyStream):
    def __init__(self, loop: asyncio.AbstractEventLoop, interval: float):
        super().__init__()
        self.interval = interval
        self._loop = loop
        self._future: typing.Optional[asyncio.Future] = None

    def _create_future(self):
        async def simulated_data():
            while True:
                for i in range(100):
                    await asyncio.sleep(self.interval)
                    self._response_received({'param', 42 + i/100})
        t = asyncio.run_coroutine_threadsafe(simulated_data(), self._loop)
        return asyncio.wrap_future(t, loop=self._loop)

    def start(self, subs):
        super().start(subs)
        if self._future is not None:
            # TODO: Possibly remove the fact that restarting raises (it
            #  probably doesn't matter if already started).
            raise RuntimeError("The stream has already been started")
        self._future = self._create_future()

    def stop(self, subs):
        super().stop(subs)
        if self._future is not None:
            # Note: It is not possible to pause a future without using an event,
            # and it is important that a coroutine doesn't continue to run
            # when the loop exits, therefore we terminate
            # and re-create the future for each start/stop.
            self._future.cancel()
            self._future = None


class AsyncIOProvider(BaseProvider):
    def __init__(
            self,
            *,
            loop: typing.Optional[asyncio.AbstractEventLoop] = None,
            interval: float = 0.25,
    ):
        if loop is None:
            loop = asyncio.get_running_loop()
        self._loop: asyncio.AbstractEventLoop = loop
        self.interval = interval
        super().__init__()

    @classmethod
    def create_background_loop(cls) -> asyncio.AbstractEventLoop:
        """
        Setup a new event loop on a background thread.

        This is a utility classmethod which is useful when not running
        an AsyncIOProvider with an asyncio client.

        """
        loop = asyncio.new_event_loop()

        def start_event_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()

        t = threading.Thread(
            target=start_event_loop,
            daemon=True,
        )
        t.start()
        return loop

    def _get_property(self, query: "PropertyAccessQuery") -> concurrent.futures.Future:
        async def set_after(delay, value):
            await asyncio.sleep(delay)
            return value

        t = asyncio.run_coroutine_threadsafe(
            set_after(self.interval, {'param', 42}),
            self._loop,
        )
        return t

    def _create_property_stream(self, query: "PropertyAccessQuery") -> AsyncIOPropertyStream:
        subs = AsyncIOPropertyStream(self._loop, interval=self.interval)
        return subs
