import typing

from ... import data

if typing.TYPE_CHECKING:
    from ...data import PropertyAccessQuery, PropertyRetrievalResponse
    from ...providers._core import BasePropertyStream, BaseProvider
    from ...providers._middleware import StreamMiddleware

    SelectorArgumentType = typing.Union[str, data.Selector]


class BaseSubscription:
    """
    The client side subscription type.

    """
    def __init__(self, property_stream: "BasePropertyStream", query: "PropertyAccessQuery"):
        self._property_stream = property_stream
        self._query = query

    @property
    def query(self) -> "PropertyAccessQuery":
        return self._query

    def _response_received(self, response: "PropertyRetrievalResponse"):
        # Dummy method for now to implement the StreamResponseHandlerProtocol protocol.
        return self.subs_response_received(response)

    def subs_response_received(self, response: "PropertyRetrievalResponse"):
        # Called when the property stream has received data. For immediate
        # Subscription types (synchronous, callback, etc.) work may be done to
        # process the response in this method. Ideally it wouldn't block, but
        # that is acceptable for synchronous cases. For asynchronous types, you may
        # want to set up a condition that can be awaited, or add tasks to the
        # event loop, for example.
        # Note that the thread from which this is called depends on the provider.
        pass

    def start(self):
        # Start the subscription **for this client**. Does not affect other clients
        # which may be looking at the same property stream.
        self._property_stream.start(self)

    def stop(self):
        # Start the subscription **for this client**. Does not affect other clients
        # which may be looking at the same property stream.
        self._property_stream.stop(self)


class BaseSubscriptionPool:
    """
    A container for subscriptions.

    """
    def __init__(self):
        self._subs: typing.List[BaseSubscription] = []

    def _add_subscription(self, subs: BaseSubscription):
        self._subs.append(subs)


class BaseClient:
    def __init__(self, *, provider: "BaseProvider"):
        self._provider = provider
        self.subscriptions = BaseSubscriptionPool()
        self._stream_middlewares: typing.List[StreamMiddleware] = []

    def subscribe(
            self,
            *,
            device: str,
            prop: str,
            selector: "SelectorArgumentType" = data.Selector(''),
    ) -> BaseSubscription:
        selector = self._ensure_selector(selector)
        query = self._build_query(device, prop, selector)
        stream = self._create_property_stream(query)
        subs = self._build_subscription(stream, query)
        self.subscriptions._add_subscription(subs)
        return subs

    @property
    def provider(self) -> "BaseProvider":
        return self._provider

    def _create_property_stream(self, query: data.PropertyAccessQuery) -> "BasePropertyStream":
        data_stream = self.provider._create_property_stream(query)
        for middleware in self._stream_middlewares:
            data_stream = middleware.wrap_stream(data_stream)
        return data_stream

    def _ensure_selector(self, selector: "SelectorArgumentType") -> data.Selector:
        if not isinstance(selector, data.Selector):
            return data.Selector(selector)
        return selector

    def _build_subscription(self, stream: "BasePropertyStream", query: "PropertyAccessQuery"):
        return BaseSubscription(stream, query)

    def _build_query(
            self,
            device: str,
            prop: str,
            selector: data.Selector,
    ) -> data.PropertyAccessQuery:
        # TODO: Expose the data_filters argument, when supported by public API
        return data.PropertyAccessQuery(device=device, prop=prop, selector=selector)
