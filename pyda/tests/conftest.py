from unittest import mock

import pytest


@pytest.fixture
def dummy_provider():
    return mock.MagicMock()
