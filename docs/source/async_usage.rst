Asynchronous actions
====================

Each client API allows synchronous actions, similar to those of :class:`~pyda.SimpleClient` for convenience.
However, their main target is asynchronous actions:

- Subscriptions
- Asynchronous GETs
- Asynchronous SETs

We provide a number of asynchronous client APIs:

* `CallbackClient`_
* `AsyncIOClient`_


CallbackClient
--------------

The most basic type of asynchronous client is callback-based client. It is the easiest to reason about,
but multitude of callbacks can be concerning in some situations, which in many programming languages led to the search
for a better APIs, and resulted in adoption of async-await paradigm (:mod:`asyncio` in Python), allowing to write
asynchronous code in a sequential manner (see `AsyncIOClient`_).

Taking the subscription example from :doc:`usage`, the usage of the :class:`~pyda.CallbackClient` looks as follows::

    import pyda
    import pyda_japc

    client = pyda.CallbackClient(provider=pyda_japc.JapcProvider())
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
forever? This use case can be better approached via `AsyncIOClient`_.

.. note:: This does not present a problem in GUI applications, because each GUI application has its own event loop,
          hence Python process does not finish until user quits the application.


AsyncIOClient
-------------

Similar example as above can be rewritten with Python async syntax using a :class:`~pyda.AsyncIOClient`::

    import pyda
    import pyda_japc

    client = pyda.AsyncIOClient(provider=pyda_japc.JapcProvider())

    sub = client.subscribe(device='SOME.DEVICE',
                           prop='SomeProperty',
                           selector='SOME.TIMING.USER)
    sub.start()

    with sub:
        async for response in sub:
            print(response)

As you can see, aside some asyncio-specific syntax keywords, this code is almost identical to that of :doc:`usage`
that uses blocking subscriptions of :class:`SimpeClient`. Similarly, we can merge responses from several subscriptions
into a single loop using a context manager::

    with client.subscriptions:
        async for response in client.subscriptions:
            print(response)

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
        with sub:
            async for data in sub:
                print(data)

    asyncio.run(coro())

So far we've reviewed requests to devices open to everyone. For RBAC-protected access, move on to :doc:`rbac`.
