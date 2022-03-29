import time
import unittest.mock

import pytest

from pyda import AsyncIOClient, CallbackClient, SimpleClient

from .some_sync_provider import SomeSynchronousProvider


def test_simple_client():
    provider = SomeSynchronousProvider()
    cli = SimpleClient(provider=provider)
    result = cli.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


@pytest.mark.asyncio
async def test_asyncio_client():
    provider = SomeSynchronousProvider()
    cli = AsyncIOClient(provider=provider)
    result = await cli.get(device='some-device', prop='some-property')
    assert result == {'param', 42}


@pytest.mark.asyncio
async def test_callback_client():
    provider = SomeSynchronousProvider()
    cli = CallbackClient(provider=provider)
    callback = unittest.mock.Mock()
    cli.get(device='some-device', prop='some-property', callback=callback)
    callback.assert_not_called()
    time.sleep(0.5)
    callback.assert_called_once_with({'param', 42})
