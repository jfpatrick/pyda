"""
Documentation for the pyda package

"""

from ._version import version as __version__  # noqa
from .clients.asyncio._asyncio import AsyncIOClient
from .clients.callback._callback import CallbackClient
from .clients.simple._simple import SimpleClient

AsyncIOClient.__module__ = __name__
CallbackClient.__module__ = __name__
SimpleClient.__module__ = __name__
