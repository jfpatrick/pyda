.. _usage:

Usage
=====

PyDA has a plugin design, which means it is possible to extend PyDA to get & set device-property data from a number of sources.
These plugins are called :class:`pyda_core.DeviceProviders`.

Furthermore, pyda exposes a number of different APIs to allow you to interact with those DeviceProviders.

Let's start by using a common device provider at CERN, the JAPC provider, along with a callback-based API::

    import pyda
    import pyda_japc

    client = pyda.CallbackClient(provider=pyda_japc.Provider(accelerator='LHC'))

With such a client, we can get a data property from a particular device::

    data = client.get('some-device/some-property')

The returned type is a :class:`pyda_core.model.AcquiredDataTypeValue`, which is an immutable version of a :class:`pyda_core.model.DataTypeValue`.
A :class:`pyda_core.model.DataTypeValue` is a strongly-typed dictionary-like data type. The API is intentionally similar to that of a dictionary::

    >>> print(data.keys())
    [...]

We can get hold of a particular field from the property with standard dictionary-like access. For example::

    data['some-field']

Note that data is immutable, so you cannot change existing values. Instead we must copy the data in order to modify the property::

    new_data = data.mutable_copy()
    new_data['some-field'] = 15

With this we can set the whole property back onto the device::

    client.set('some-device/some-property', new_data)

Had the property allowed "partial setting" (as can be determined from :attr:`DataTypeValue.accepts_partial <pyda_core.model.DataTypeValue.accepts_partial>`),
we could alternatively have simply set the new field directly::

    client.set('some-device/some-property', {'some-field': 15})
    OR ?
    client['some-device/some-property'] = {'some-field': 15}

Subscriptions
-------------

It is common to want to listen and react to ongoing changes to a device property.
Subscriptions are used for this purpose. Most providers guarantee an initial value is given even if the device itself hasn't changed its value - this behaviour is provider specific (TO BE DETERMINED).

The simplest way to subscribe to data is to use a callback function::

    client.subscribe('some-device/some-property', callback=print)

This will result in all properties being printed to the stdout when new values are received.

You can prevent the subscription from automatically starting, and can control its lifecycle explicitly.::

    subs = client.subscribe('some-device/some-property', callback=print, autostart=False)
    subs.start()
    subs.stop()

Note that the ``CallbackClient`` is implicitly stateful, and holds on to a reference of the subscription::

    for subs in client.subscriptions:
        print(f'{subs.device_name}/{subs.property_name}')
    ...

There are other types of clients, which have a different subscription API. For example, you can use Python's asynchronous API::

    async_cli = client.FutureClient(provider=pyda_japc.Provider(inca_server='lhc'))

    subscription = async_cli.subscribe('some-device/some-property')
    async for data in subscription:
        print('data:', data)

Please see the :ref:`async_client` documentation for more details and examples.

Similarly, a generator based subscription is possible with the :class:`pyda.GeneratorClient`::

    gen_cli = client.GeneratorClient(provider=pyda_japc.Provider(inca_server='lhc'))

    subscription = gen_cli.subscribe('some-device/some-property')
    print('data:', next(data))

Note that it is not possible to know in advance if more data will arrive to the generator, and waiting on data is a non-parallelisable blocking call, so the generator approach is not recommended beyond an interactive context.