import asyncio
import typing

from ...data import Selector
from ..core import BaseClient, BaseSubscription, BaseSubscriptionPool

if typing.TYPE_CHECKING:
    from ...data import PropertyAccessResponse
    from ...providers._core import BasePropertyStream
    from ..core._core import SelectorArg


class AsyncIOSubscription(BaseSubscription):
    def __init__(self, property_stream: "BasePropertyStream", loop: asyncio.AbstractEventLoop):
        self._q: asyncio.Queue = asyncio.Queue()
        self._enabled_queues: typing.List[asyncio.Queue] = []
        self._loop = loop
        super().__init__(property_stream)

    def subs_response_received(self, response: "PropertyAccessResponse"):
        for queue in self._enabled_queues:
            # TODO: Do we need to hold on to a reference to this future?
            asyncio.run_coroutine_threadsafe(queue.put(response), loop=self._loop)

    async def __aenter__(self):
        self._enabled_queues.append(self._q)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._enabled_queues.remove(self._q)

    def __aiter__(self):
        # TODO: Check that the pool is doing this inside a managed context.
        return self

    async def __anext__(self) -> "PropertyAccessResponse":
        resp = await self._q.get()
        # TODO: Is it possible that multiple iterations are taking place?
        self._q.task_done()
        return resp


class AsyncIOSubscriptionPool(BaseSubscriptionPool):
    def __init__(self):
        super().__init__()
        self._q: asyncio.Queue = asyncio.Queue()

    async def __aenter__(self):
        for sub in self._subs:
            sub._enabled_queues.append(self._q)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for sub in self._subs:
            sub._enabled_queues.remove(self._q)

    def __aiter__(self):
        # TODO: Check that the pool is doing this inside a managed context.
        return self

    async def __anext__(self):
        resp = await self._q.get()
        # TODO: Is it possible that multiple iterations are taking place?
        self._q.task_done()
        return resp


class AsyncIOClient(BaseClient):
    def __init__(self, *, provider):
        super().__init__(provider=provider)
        # TODO: Simplify by injecting the type into the base client.
        self.subscriptions = AsyncIOSubscriptionPool()

    async def get(
            self,
            *,
            device: str,
            prop: str,
            selector: "SelectorArg" = Selector(''),
    ) -> "PropertyAccessResponse":
        selector = self._ensure_selector(selector)
        query = self._build_query(device, prop, selector)
        future = self.provider._get_property(query)
        return await asyncio.wrap_future(future)

    def subscribe(
            self,
            *,
            device: str,
            prop: str,
            selector: "SelectorArg" = Selector(''),
    ) -> AsyncIOSubscription:
        selector = self._ensure_selector(selector)
        query = self._build_query(device, prop, selector)
        subs = AsyncIOSubscription(
            self._create_property_stream(query),
            # Note: Must be called on the loop's thread.
            # Perhaps we can do better than this though...
            asyncio.get_running_loop(),
        )
        self.subscriptions._subs.append(subs)
        return subs
