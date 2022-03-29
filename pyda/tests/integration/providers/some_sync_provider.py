import concurrent.futures
import time
import typing

from pyda.providers._core import BaseProvider

if typing.TYPE_CHECKING:
    from pyda.data import PropertyAccessQuery


class SomeSynchronousProvider(BaseProvider):
    # Providers aren't allowed to block, so we setup a pool to do the synchronous work.
    def __init__(self, interval: float = 0.1):
        super().__init__()
        # This thread-pool exists purely to simulate some other process (such as JAPC)
        # for which we have no control of the threads in which the callbacks being triggered.
        # It doesn't make sense for this particular pool to be the same as a potential thread
        # pool of a client.
        self._pool = concurrent.futures.ThreadPoolExecutor()
        self._interval = interval
        self._value = 42

    def _get_property(self, query: "PropertyAccessQuery") -> concurrent.futures.Future:
        def get_data():
            # A blocking function which gets data.
            time.sleep(self._interval)
            return {'param', self._value}
        return self._pool.submit(get_data)

    def _set_property(
            self,
            query: "PropertyAccessQuery",
            value: typing.Any,
    ) -> concurrent.futures.Future:
        def set_data():
            # A blocking function which sets data.
            time.sleep(self._interval)
            self._value = value
            return {'some-header': {}}
        return self._pool.submit(set_data)
