.. _usage:

Usage
=====

PyDA has a layered design, separating user-facing client API from backend. Selection of client APIs allows
user to pick the right tool for the job, based on complexity/approach/syntax objectives or preferences.

Pluggable architecture for backends makes it possible to extend PyDA in order to send & receive device-property data
to/from a number of sources. These plugins are called "PyDA providers".

.. note:: link required for "PyDA providers"

To better illustrate the utility, let's take an example of using a common device-data provider (:class:`pyda_japc.JapcProvider`),
combined with a simple synchronous API (:class:`pyda.SimpleClient`) for convenient and easy to reason about data flow,
especially in interactive and scripting contexts::

    import pyda
    import pyda_japc

    client = pyda.SimpleClient(provider=pyda_japc.JapcProvider())

With such a client, we can get a data property from a particular device::

    response = client.get(device='SOME.DEVICE',
                          prop='SomeProperty',
                          selector='SOME.TIMING.USER')

The returned type is a :class:`pyda.data.PropertyRetrievalResponse`, which is an envelope containing information
about requested information, returned data and meta-data or the exception. To access a value from this envelope,
simply access :attr:`~pyda.data.PropertyRetrievalResponse.value` property. If data was not retrieved and exception
was caught, this action will raise::

    try:
        my_value = response.value
    except pyda.data.PropertyAccessError as e:
        my_exception = e

The same exception (without raising) can be also obtained via :attr:`~pyda.data.PropertyRetrievalResponse.exception`
property::

    my_exception = response.exception

The value type is an immutable version of :class:`pyds_model.DataTypeValue` purposed for incoming data.
A :class:`pyds_model.DataTypeValue` provides strongly-typed dictionary-like data structures. The API is intentionally
similar to that of a dictionary::

    >>> print(value.keys())
    [...]

We can get hold of a particular field from the property with standard dictionary-like access. For example::

    value['some-field']
    # or
    value.get('some-field', default='Fallback value')

Note that ``value`` is immutable, so you cannot change existing values.
Instead we must expose the data in a different container in order to modify the field values::

    new_data = value.mutable_data()
    new_data['some-field'] = 15

With this we can feed the property data back to the device::

    client.set(device='SOME.DEVICE',
               prop='SomeProperty',
               selector='SOME.TIMING.USER',
               value=new_data)

Had the property allowed "partial setting" (as can be determined from
:attr:`DataTypeValue.accepts_partial <pyds_model.DataTypeValue.accepts_partial>`),
we could alternatively have simply set the new field directly::

    client.set(device='SOME.DEVICE',
               prop='SomeProperty',
               selector='SOME.TIMING.USER',
               value={'some-field': 15})

.. note:: All client APIs have keyword-only arguments. This is done to reduce the likelihood of breaking changes in the
          prototype, should the argument composition change in the future.
