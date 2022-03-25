import pytest

import pyda
from pyda import data
from pyda.clients import simple


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
def test__SimpleClient__get(kwargs, dummy_provider, expected_query_args):
    cli = pyda.SimpleClient(provider=dummy_provider)
    cli.get(**kwargs)
    dummy_provider._get_property.assert_called_once_with(
        data.PropertyAccessQuery(**expected_query_args),
    )


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
def test__SimpleClient__subscribe(kwargs, dummy_provider, expected_query_args):
    cli = pyda.SimpleClient(provider=dummy_provider)
    sub = cli.subscribe(**kwargs)
    dummy_provider._create_property_stream.assert_called_once_with(
        data.PropertyAccessQuery(**expected_query_args),
    )
    assert isinstance(sub, simple.SimpleSubscription)
