import concurrent.futures
import typing
import weakref

from .. import core
from ... import data

if typing.TYPE_CHECKING:
    from ...data import PropertyRetrievalResponse, PropertyUpdateResponse
    from ...providers._core import BasePropertyStream
    from ..core._core import SelectorArgumentType


RetrievalCallback = typing.Callable[["PropertyRetrievalResponse"], None]
UpdateCallback = typing.Callable[["PropertyUpdateResponse"], None]


class CallbackSubscription(core.BaseSubscription):
    def __init__(
            self, property_stream: "BasePropertyStream",
            client: "CallbackClient",
            callback: RetrievalCallback,
    ):
        self._cli = weakref.ref(client)
        self._callback = callback
        super().__init__(property_stream)

    def subs_response_received(self, response: "PropertyRetrievalResponse"):
        cli = self._cli()
        if cli:
            # TODO: Do we need to hold on to a reference to this future?
            cli._pool.submit(self._callback, response)


class CallbackClient(core.BaseClient):
    def __init__(self, *, provider):
        super().__init__(provider=provider)
        # The thread-pool in which callbacks are run. By default, we have just one worker in the
        # pool, this could be more workers if thread-safe callbacks. Should be user configurable.
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def get(
            self,
            *,
            device: str,
            prop: str,
            callback: RetrievalCallback,
            selector: "SelectorArgumentType" = data.Selector(''),
    ) -> None:
        selector = self._ensure_selector(selector)
        query = self._build_query(device, prop, selector)
        future = self.provider._get_property(query)

        def run_callback(future):
            self._pool.submit(callback, future.result())

        future.add_done_callback(run_callback)

    def set(
            self,
            *,
            device: str,
            prop: str,
            value: typing.Any,
            callback: UpdateCallback,
            selector: "SelectorArgumentType" = data.Selector(''),
    ) -> None:
        selector = self._ensure_selector(selector)
        query = self._build_query(device, prop, selector)
        future = self.provider._set_property(query, value)

        def run_callback(future):
            self._pool.submit(callback, future.result())

        future.add_done_callback(run_callback)

    def subscribe(  # type: ignore[override]
            self,
            *,
            device: str,
            prop: str,
            callback: RetrievalCallback,
            selector: "SelectorArgumentType" = data.Selector(''),
    ) -> CallbackSubscription:
        selector = self._ensure_selector(selector)
        query = self._build_query(device, prop, selector)
        subs = CallbackSubscription(
            self._create_property_stream(query),
            self,
            callback,
        )
        self.subscriptions._subs.append(subs)
        return subs
