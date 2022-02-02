.. _async_client:

PyDA asynchronous client
========================

PyDA has an asynchronous client built-in, which allows for efficiently getting and setting data without
blocking the interpreter and allowing execution of other activities in parallel.

The asynchronous API in Python is best used when data I/O performance plays a significant role in the overall performance.

First, we create an asynchronous API, in this case using the JAPC provider, with::

    import pyda
    import pyda_japc

    client = pyda.AsyncClient(provider=pyda_japc.Provider(accelerator='LHC'))

.. note::

    From a standard REPL you will need to remove the final await call and run with ``asyncio.run(cmd)`` to run the following examples.
    From a REPL which automatically calls coroutines, such as IPython, no such call is needed.

Once we have a client, we can get and set asynchronously::

    await client.get('device/some-property')

Similarly::

    await client.set('device/some-property', {'some-field': 15})

For subscriptions, we first create the subscription and can await multiple values::

    subs = client.subscribe('device/some-property')
    print(await subs)
    print(await subs)

It is common to want to subscribe to multiple subscriptions at the same time. Interactively, this can be done with (TO BE CHECKED)::

    subscriptions = [
        client.subscribe('device/some-property'),
        client.subscribe('another-device/some-other-property'),
    ]
    while True:
        for coro in asyncio.as_completed(subscriptions):
            data = await coro
            break
        print(data.device_name)

Synchronising subscriptions according to their time stamp or cycle stamp is out of scope for PyDA. Such functionality can be achieved as a third-party library - we will link to such a library here if/when it exists.