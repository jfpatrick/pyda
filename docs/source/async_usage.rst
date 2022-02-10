Asynchronous actions
====================

Each client API allows synchronous actions, similar to those of ``SimpleClient`` for convenience. However, their
main target is asynchronous actions:

- Subscriptions
- Asynchronous GETs
- Asynchronous SETs

We provide a number of asynchronous client APIs:

* `CallbackClient`_
* `CoroutineClient`_


CallbackClient
--------------

The most basic type of asynchronous client is callback-based client. It is the easiest to reason about,
but multitude of callbacks can be concerning in some situations, which in many programming languages led to the search
for a better APIs, and resulted in adoption of async-await paradigm (:mod:`asyncio` in Python), allowing to write
asynchronous code in a sequential manner (see `CoroutineClient`_).

Taking the callback example from :doc:`usage`, the usage of the ``CallbackClient`` looks as follows::

    import pyda
    from pyda_japc import JAPCProvider

    client = pyda.CallbackClient(provider=JAPCProvider())
    sub = client.subscribe(device='SOME.DEVICE',
                           prop='SomeProperty',
                           selector='SOME.TIMING.USER',
                           callback=print)
    sub.start()

This will result in property data being printed to the ``stdout`` whenever subscription notifications are received.

.. note:: Subscription notifications are asynchronous, therefore when put into a simple sequential script, this code
          is unlikely to produce any output, because Python interpreter will finish operation before any notification
          is received.

To make this code work in a simple script, we must put an artificial wait to allow subscriptions to execute::

    import time
    time.sleep(5)

JAPC callbacks are executed in a thread pool, therefore there's no harm to blocking current thread. However, it's
unclear, what is a good time value to put into ``sleep`` function. And what if we wanted to keep printing subscriptions
forever? This use case can be better approached via `CoroutineClient`_.

.. note:: This does not present a problem in GUI applications, because each GUI application has its own event loop,
          hence Python process does not finish until user quits the application.


CoroutineClient
---------------

Similar example as above can be rewritten with Python async syntax using a ``CoroutineClient``::

    import pyda
    from pyda_japc import JAPCProvider

    client = pyda.CoroutineClient(provider=JAPCProvider())

    sub = client.subscribe(device='SOME.DEVICE',
                           prop='SomeProperty',
                           selector='SOME.TIMING.USER)
    sub.start()

    async for data in sub:
        print(data)

.. note:: Async code cannot be used in the global scope of the Python script, and will need to be launched inside the
          event loop.

Rewriting the example above to contain a coroutine that can be run in the main event loop, we can use ``asyncio.run()``
shortcut, which schedules a coroutine in the newly created event loop, and will wait until the coroutine is
finished. In this particular example, subscription will indefinitely produce data, hence the script will keep printing
values forever, unless the user kills the process::

    ...

    import asyncio

    sub = client.subscribe(device='SOME.DEVICE',
                           prop='SomeProperty',
                           selector='SOME.TIMING.USER)
    sub.start()

    async def coro():
        async for data in sub:
            print(data)

    asyncio.run(coro())
