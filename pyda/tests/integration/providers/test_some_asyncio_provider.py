import time
import unittest.mock

import pytest

from pyda import AsyncIOClient, CallbackClient, SimpleClient

from .some_asyncio_provider import AsyncIOProvider


def test_no_event_loop_available():
    with pytest.raises(RuntimeError):
        AsyncIOProvider()


def test_simple_client():
    background_loop = AsyncIOProvider.create_background_loop()
    provider = AsyncIOProvider(loop=background_loop)
    cli = SimpleClient(provider=provider)
    result = cli.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


def test_simple_client_subs():
    background_loop = AsyncIOProvider.create_background_loop()
    provider = AsyncIOProvider(loop=background_loop, interval=0.1)
    cli = SimpleClient(provider=provider)
    subs = cli.subscribe(device='some-device', prop='some-property')
    subs.start()
    with subs:
        for response in subs:
            assert response == {'param', 42}
            break
        assert next(subs) == {'param', 42.01}
    subs.stop()
    subs.start()
    with cli.subscriptions:
        for response in cli.subscriptions:
            assert response == {'param', 42}
            break
        assert next(cli.subscriptions) == {'param', 42.01}


@pytest.mark.asyncio
async def test_asyncio_client(monkeypatch):
    provider = AsyncIOProvider(interval=0)
    cli = AsyncIOClient(provider=provider)
    result = await cli.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


def test_callback_client():
    provider = AsyncIOProvider(loop=AsyncIOProvider.create_background_loop(), interval=0.05)
    cli = CallbackClient(provider=provider)
    callback = unittest.mock.Mock()
    cli.get(device='some-device', prop='some-property', callback=callback)
    callback.assert_not_called()
    time.sleep(0.1)
    callback.assert_called_once_with({'param', 42})


@pytest.mark.asyncio
async def test_asyncio_client_subs():
    provider = AsyncIOProvider()
    cli = AsyncIOClient(provider=provider)
    subs = cli.subscribe(device='some-device', prop='some-property')
    subs.start()
    async with subs:
        async for resp in subs:
            assert resp == {'param', 42}
            break
    # Note we can't start and stop asyncio providers (but we currently
    # can with callback providers).
    subs.stop()
    subs.start()
    async with cli.subscriptions:
        async for resp in cli.subscriptions:
            assert resp == {'param', 42}
            break
