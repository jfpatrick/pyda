import concurrent.futures
import time
import typing

from pyda.providers._core import BaseProvider

if typing.TYPE_CHECKING:
    from pyda.data import PropertyAccessQuery


class SomeSynchronousProvider(BaseProvider):
    # Providers aren't allowed to block, so we setup a pool to do the synchronous work.
    def __init__(self):
        super().__init__()
        # This thread-pool exists purely to simulate some other process (such as JAPC)
        # for which we have no control of the threads in which the callbacks being triggered.
        # It doesn't make sense for this particular pool to be the same as a potential thread
        # pool of a client.
        self._pool = concurrent.futures.ThreadPoolExecutor()

    def _get_property(self, query: "PropertyAccessQuery") -> concurrent.futures.Future:
        def get_data():
            # A blocking function which gets data.
            time.sleep(0.4)
            return {'param', 42}
        return self._pool.submit(get_data)
