.. _usage:

Usage
=====

PyDA has a layered design, separating user-facing client API from backend. Selection of client APIs allows
user to pick the right tool for the job, based on complexity/approach/syntax objectives or preferences.

Pluggable architecture for backends makes it possible to extend PyDA in order to send & receive device-property data
to/from a number of sources. These plugins are called "PyDA providers".

To better illustrate the utility, let's take an example of using a common device provider, JAPC, along with a
callback-based API (that makes it easy to reason about data flow, especially in simple scripts)::

    import pyda
    import pyda_japc

    client = pyda.CallbackClient(provider=pyda_japc.Provider.shared_provider())

With such a client, we can get a data property from a particular device::

    data = client.get('SOME.DEVICE/SomeProperty')

The returned type is a :class:`pyda_core.model.AcquiredDataTypeValue`, which is an immutable version of a
:class:`pyda_core.model.DataTypeValue` purposed for incoming data. A :class:`pyda_core.model.DataTypeValue` provides
strongly-typed dictionary-like data structures. The API is intentionally similar to that of a dictionary::

    >>> print(data.keys())
    [...]

We can get hold of a particular field from the property with standard dictionary-like access. For example::

    data['some-field']

Note that data is immutable, so you cannot change existing values.
Instead we must expose the data in a different container in order to modify the field values::

    new_data = data.mutable_data()
    new_data['some-field'] = 15

With this we can feed the property data back to the device::

    client.set('SOME.DEVICE/SomeProperty', new_data)

Had the property allowed "partial setting" (as can be determined from
:attr:`DataTypeValue.accepts_partial <pyda_core.model.DataTypeValue.accepts_partial>`),
we could alternatively have simply set the new field directly::

    client.set('SOME.DEVICE/SomeProperty', {'some-field': 15})
