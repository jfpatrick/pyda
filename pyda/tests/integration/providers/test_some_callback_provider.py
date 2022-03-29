import time
import unittest.mock

import pytest

from pyda import AsyncIOClient, CallbackClient, SimpleClient

from .some_callback_provider import SomeCallbackProvider


@pytest.fixture
def simple_client():
    provider = SomeCallbackProvider()
    return SimpleClient(provider=provider)


@pytest.fixture
def callback_client():
    provider = SomeCallbackProvider()
    return CallbackClient(provider=provider)


@pytest.fixture
def asyncio_client():
    provider = SomeCallbackProvider()
    return AsyncIOClient(provider=provider)


def test_simple_client__get(simple_client):
    result = simple_client.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


def test_simple_client__set(simple_client):
    result = simple_client.set(device='some-device', prop='some-property', value='some-value')
    assert result == {'some-header': {}}
    result = simple_client.get(device='some-device', prop='some-property')
    assert result == {'param', 'some-value'}


@pytest.mark.asyncio
async def test_asyncio_client__get(asyncio_client):
    result = await asyncio_client.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


@pytest.mark.asyncio
async def test_asyncio_client__set(asyncio_client):
    result = await asyncio_client.set(
        device='some-device', prop='some-property', value='some-value',
    )
    assert result == {'some-header': {}}
    result = await asyncio_client.get(device='some-device', prop='some-property')
    assert result == {'param', 'some-value'}


def test_callback_client__get(callback_client):
    callback = unittest.mock.Mock()
    callback_client.get(device='some-device', prop='some-property', callback=callback)
    callback.assert_not_called()
    time.sleep(0.5)
    callback.assert_called_once_with({'param', 42})


def test_callback_client__set(callback_client):
    callback = unittest.mock.Mock()
    callback_client.set(
        device='some-device', prop='some-property', callback=callback, value='some-value',
    )
    callback.assert_not_called()
    time.sleep(0.5)
    callback.assert_called_once_with({'some-header': {}})

    callback = unittest.mock.Mock()
    callback_client.get(device='some-device', prop='some-property', callback=callback)
    time.sleep(0.5)
    callback.assert_called_once_with({'param', 'some-value'})


def test_simple_client__subs(simple_client):
    subs = simple_client.subscribe(device='some-device', prop='some-property')
    subs.start()
    with subs:
        for response in subs:
            assert response == {'param', 42}
            break
    subs.stop()
    subs.start()
    with simple_client.subscriptions:
        for response in simple_client.subscriptions:
            assert response == {'param', 42.01}
            break
        assert next(simple_client.subscriptions) == {'param', 42.02}


def test_callback_client__subs(callback_client):
    callback = unittest.mock.Mock()
    subs = callback_client.subscribe(device='some-device', prop='some-property', callback=callback)
    subs.start()
    callback.assert_not_called()
    time.sleep(0.3)
    callback.assert_called_once_with({'param', 42})
    subs.stop()


@pytest.mark.asyncio
async def test_asyncio_client__subs(asyncio_client):
    # TODO: If we are going to verify that a subscription is possible,
    #  perhaps this should be ``await cli.subscribe(...)``.
    subs = asyncio_client.subscribe(device='some-device', prop='some-property')
    subs.start()
    async with subs:
        async for resp in subs:
            assert resp == {'param', 42}
            break
    subs.stop()
    subs.start()
    async with asyncio_client.subscriptions:
        async for resp in asyncio_client.subscriptions:
            assert resp == {'param', 42 + 1 / 100}
            break
