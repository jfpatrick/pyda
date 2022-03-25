import asyncio
from unittest import mock

import pytest

import pyda
from pyda import data
from pyda.clients import asyncio as asyncio_client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs,expected_query_args", [
        (
                {'device': 'some-device', 'prop': 'some-property'},
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector(''),
                },
        ),
        (
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector(''),
                },
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector(''),
                },
        ),
        (
                {'device': 'some-device', 'prop': 'some-property', 'selector': ''},
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector(''),
                },
        ),
        (
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': 'SOME.TEST.SELECTOR',
                },
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector('SOME.TEST.SELECTOR'),
                },
        ),
        (
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector('ANOTHER.TEST.SELECTOR'),
                },
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector('ANOTHER.TEST.SELECTOR'),
                },
        ),
    ],
)
async def test__AsyncIOClient__get(kwargs, dummy_provider, expected_query_args):
    res = asyncio.Future()
    res.set_result(mock.MagicMock())
    dummy_provider._get_property.return_value = res
    cli = pyda.AsyncIOClient(provider=dummy_provider)
    await cli.get(**kwargs)
    dummy_provider._get_property.assert_called_once_with(
        data.PropertyAccessQuery(**expected_query_args),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs,expected_query_args", [
        (
                {'device': 'some-device', 'prop': 'some-property'},
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector(''),
                },
        ),
        (
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector(''),
                },
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector(''),
                },
        ),
        (
                {'device': 'some-device', 'prop': 'some-property', 'selector': ''},
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector(''),
                },
        ),
        (
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': 'SOME.TEST.SELECTOR',
                },
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector('SOME.TEST.SELECTOR'),
                },
        ),
        (
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector('ANOTHER.TEST.SELECTOR'),
                },
                {
                    'device': 'some-device',
                    'prop': 'some-property',
                    'selector': data.Selector('ANOTHER.TEST.SELECTOR'),
                },
        ),
    ],
)
async def test__AsyncIOClient__subscribe(kwargs, dummy_provider, expected_query_args):
    cli = pyda.AsyncIOClient(provider=dummy_provider)
    sub = cli.subscribe(**kwargs)
    dummy_provider._create_property_stream.assert_called_once_with(
        data.PropertyAccessQuery(**expected_query_args),
    )
    assert isinstance(sub, asyncio_client.AsyncIOSubscription)
