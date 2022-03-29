import concurrent.futures
import threading
import time
import typing

from pyda.providers._core import BasePropertyStream, BaseProvider

if typing.TYPE_CHECKING:
    from pyda.data import PropertyAccessQuery


class CallbackPropertyStream(BasePropertyStream):
    def __init__(self, query: "PropertyAccessQuery", interval: float):
        super().__init__()
        self.interval = interval
        self._is_running = threading.Event()

        def simulated_data():
            while True:
                self._is_running.wait()
                for i in range(100):
                    time.sleep(self.interval)
                    self._response_received({'param', 42 + i/100})
                    if not self._is_running.is_set():
                        break
        self._thread = threading.Thread(target=simulated_data, daemon=True)
        self._thread.start()

    def start(self, stream_handler):
        super().start(stream_handler)
        self._is_running.set()

    def stop(self, stream_handler):
        super().stop(stream_handler)
        if not self._stream_handlers:
            # We only stop when there are no more watching handlers.
            self._is_running.clear()


class SomeCallbackProvider(BaseProvider):
    def __init__(self, *, interval: float = 0.25):
        super().__init__()
        self._value = 42
        #: The interval for new subscriptions, and get/set responses. Does not
        #: affect existing subscriptions.
        self.interval = interval

    def _get_property(self, query: "PropertyAccessQuery") -> concurrent.futures.Future:
        # A non-blocking get.
        future: concurrent.futures.Future = concurrent.futures.Future()

        def get_value():
            future.set_result({'param', self._value})

        # Simulate a system which does callbacks by calling the get_value
        # function after ``self.interval`` seconds.
        t = threading.Timer(self.interval, get_value)
        t.start()
        return future

    def _set_property(
            self,
            query: "PropertyAccessQuery",
            value: typing.Any,
    ) -> concurrent.futures.Future:
        # A non-blocking set.
        future: concurrent.futures.Future = concurrent.futures.Future()

        # Simulate a system which does callbacks by calling the set_value
        # function after ``self.interval`` seconds.
        def set_value():
            self._value = value
            future.set_result({'some-header': {}})

        t = threading.Timer(self.interval, set_value)
        t.start()
        return future

    def _create_property_stream(self, query: "PropertyAccessQuery") -> CallbackPropertyStream:
        subs = CallbackPropertyStream(query, self.interval)
        return subs
