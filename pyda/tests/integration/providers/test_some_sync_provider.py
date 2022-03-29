import time
import unittest.mock

import pytest

from pyda import AsyncIOClient, CallbackClient, SimpleClient

from .some_sync_provider import SomeSynchronousProvider


@pytest.fixture
def simple_client():
    provider = SomeSynchronousProvider()
    return SimpleClient(provider=provider)


@pytest.fixture
def callback_client():
    provider = SomeSynchronousProvider()
    return CallbackClient(provider=provider)


@pytest.fixture
def asyncio_client():
    provider = SomeSynchronousProvider()
    return AsyncIOClient(provider=provider)


def test_simple_client__get(simple_client):
    result = simple_client.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


def test_simple_client__set(simple_client):
    result = simple_client.set(device='some-device', prop='some-property', value="some-string")
    assert result == {'some-header': {}}
    result = simple_client.get(device='some-device', prop='some-property')
    assert result == {'param', 'some-string'}


@pytest.mark.asyncio
async def test_asyncio_client__get(asyncio_client):
    result = await asyncio_client.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


@pytest.mark.asyncio
async def test_asyncio_client__set(asyncio_client):
    kwargs = {'device': 'some-device', 'prop': 'some-property'}
    result = await asyncio_client.set(**kwargs, value="some-string")
    assert result == {'some-header': {}}
    result = await asyncio_client.get(**kwargs)
    assert result == {'param', 'some-string'}


def test_callback_client__get(callback_client):
    callback = unittest.mock.Mock()
    callback_client.get(device='some-device', prop='some-property', callback=callback)
    callback.assert_not_called()
    time.sleep(0.3)
    callback.assert_called_once_with({'param', 42})


def test_callback_client__set(callback_client):
    kwargs = {'device': 'some-device', 'prop': 'some-property'}
    callback = unittest.mock.Mock()
    callback_client.set(**kwargs, value="some-string", callback=callback)
    callback.assert_not_called()
    time.sleep(0.3)
    callback.assert_called_once_with({'some-header': {}})

    callback = unittest.mock.Mock()
    callback_client.get(**kwargs, callback=callback)
    time.sleep(0.3)
    callback.assert_called_once_with({'param', 'some-string'})
