import time
import unittest.mock

import pytest

from pyda import AsyncIOClient, CallbackClient, SimpleClient

from .some_callback_provider import SomeCallbackProvider


def test_simple_client():
    provider = SomeCallbackProvider()
    cli = SimpleClient(provider=provider)
    result = cli.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


@pytest.mark.asyncio
async def test_asyncio_client():
    provider = SomeCallbackProvider()
    cli = AsyncIOClient(provider=provider)
    result = await cli.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


def test_callback_client():
    provider = SomeCallbackProvider()
    cli = CallbackClient(provider=provider)
    callback = unittest.mock.Mock()
    cli.get(device='some-device', prop='some-property', callback=callback)
    callback.assert_not_called()
    time.sleep(0.5)
    callback.assert_called_once_with({'param', 42})


def test_simple_client_subs():
    provider = SomeCallbackProvider()
    cli = SimpleClient(provider=provider)
    subs = cli.subscribe(device='some-device', prop='some-property')
    subs.start()
    with subs:
        for response in subs:
            assert response == {'param', 42}
            break
    subs.stop()
    subs.start()
    with cli.subscriptions:
        for response in cli.subscriptions:
            assert response == {'param', 42.01}
            break
        assert next(cli.subscriptions) == {'param', 42.02}


def test_callback_client_subs():
    provider = SomeCallbackProvider()
    cli = CallbackClient(provider=provider)
    callback = unittest.mock.Mock()
    subs = cli.subscribe(device='some-device', prop='some-property', callback=callback)
    subs.start()
    callback.assert_not_called()
    time.sleep(0.3)
    callback.assert_called_once_with({'param', 42})
    subs.stop()


@pytest.mark.asyncio
async def test_asyncio_client_subs():
    provider = SomeCallbackProvider()
    cli = AsyncIOClient(provider=provider)
    # TODO: If we are going to verify that a subscription is possible,
    #  perhaps this should be ``await cli.subscribe(...)``.
    subs = cli.subscribe(device='some-device', prop='some-property')
    subs.start()
    async with subs:
        async for resp in subs:
            assert resp == {'param', 42}
            break
    subs.stop()
    subs.start()
    async with cli.subscriptions:
        async for resp in cli.subscriptions:
            assert resp == {'param', 42 + 1 / 100}
            break
