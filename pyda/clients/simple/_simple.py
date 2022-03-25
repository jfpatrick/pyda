import queue
import typing

from ...data import Selector
from ..core import BaseClient, BaseSubscription, BaseSubscriptionPool

if typing.TYPE_CHECKING:
    from ...data import PropertyAccessResponse
    from ...providers._core import BasePropertyStream
    from ..core._core import SelectorArg


class SimpleSubscription(BaseSubscription):
    def __init__(
            self,
            property_stream: "BasePropertyStream",
    ):
        self._q: queue.Queue = queue.Queue()
        self._enabled_queues: typing.List[queue.Queue] = []
        super().__init__(property_stream)

    def subs_response_received(self, response: "PropertyAccessResponse"):
        for q in self._enabled_queues:
            q.put(response)

    def __enter__(self):
        self._enabled_queues.append(self._q)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._enabled_queues.remove(self._q)

    def __iter__(self):
        # TODO: Check that the pool is doing this inside a managed context.
        return self

    def __next__(self) -> "PropertyAccessResponse":
        response = self._q.get()
        self._q.task_done()
        return response


class SimpleSubscriptionPool(BaseSubscriptionPool):
    def __init__(self):
        super().__init__()
        self._q = queue.Queue()

    def __enter__(self):
        for sub in self._subs:
            sub._enabled_queues.append(self._q)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for sub in self._subs:
            sub._enabled_queues.remove(self._q)

    def __iter__(self):
        # TODO: Check that the pool is doing this inside a managed context.
        return self

    def __next__(self):
        resp = self._q.get()
        self._q.task_done()
        return resp


class SimpleClient(BaseClient):
    def __init__(self, *, provider):
        super().__init__(provider=provider)
        # TODO: Simplify by injecting the type into the base client.
        self.subscriptions = SimpleSubscriptionPool()

    def get(
            self,
            *,
            device: str,
            prop: str,
            selector: "SelectorArg" = Selector(''),
    ) -> "PropertyAccessResponse":
        selector = self._ensure_selector(selector)
        query = self._build_query(device, prop, selector)
        future = self.provider._get_property(query)
        return future.result()

    def subscribe(
            self,
            *,
            device: str,
            prop: str,
            selector: "SelectorArg" = Selector(''),
    ) -> SimpleSubscription:
        selector = self._ensure_selector(selector)
        query = self._build_query(device, prop, selector)
        subs = SimpleSubscription(
            self._create_property_stream(query),
        )
        self.subscriptions._subs.append(subs)
        return subs
