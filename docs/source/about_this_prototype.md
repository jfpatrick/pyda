# About the PyDA prototype

The ``PyDA`` prototype is an attempt to refine and future-proof the client-side device access
functionality for Python users.
To achieve this we have worked on three major components so far:

 * A binding for core device property data types from the Device Server Framework (DSF)
 * A client & provider architecture to allow us to separate the "data source" from the "data access interface"
 * An implementation of a JAPC provider, backed by JPype, which is capable of delivering appropriate DSF data structures

## Comparing ``pyda-japc`` to ``PyJapc``

### Simplest case

The simplest case for a get with ``PyJapc``:
```python
import pyjapc

japc = pyjapc.PyJapc()
value = japc.getParam(f'{device}/{prop_name}')
```

And for ``pyda-japc``:

```python
import pyda
import pyda_japc

client = pyda.SimpleClient(provider=pyda_japc.JAPCProvider())
response = client.get(device=device, prop=prop_name)
value = response.value
```

There is undoubtedly more complexity in the ``pyda-japc`` version. Some of this will be simplifiable
based on the feedback we receive, and on experience gained during prototype evaluation
(for example: see the notes on keyword only arguments). Other parts are complexity that
are required to address the specific problems of PyJapc. For example, to get metadata/header
information (which is always provided by JAPC under-the-hood), we must add an extra flag to our
``getParam`` call, which in turn changes the return type:

```python
value, header = japc.getParam(f'{device}/{prop_name}', getHeader=True)
```

With PyDA, this data is already exposed in the response type, so you can simply access ``response.header``.

In general, we have striven to provide an interface which better reflects the underlying device-property
model of the control system, and at the same time provided an interface that is more adaptable when new
functionality becomes available in the control system.  Furthermore, we have designed it in such a way that
we believe we will be able to build better type safety into the core of the library, offering options for
static analysis (through tools such as mypy) and improved IDE auto-completion.


### Advantages of the PyDA API

#### Stronger typing and better future-proofing

As has already been mentioned, the PyDA interface has been designed to evolve with the control system
with an aim to minimising the number of breaking changes to the user. In addition, it is planned to provide
stronger typing of the client API and resulting data structures, allowing tools such as mypy to identify
potential issues with the API, and to provide additional context should there be a need for an API
change in the future. It is hoped that this type checking will extend to the data types for devices where
practical. This information can be taken from a number of sources, such as the CCDB or through future control
system enhancements for self-describing devices (e.g. via DSF and FESA8).

<!--
#### Opportunities for more ambitious client APIs

A more ambitious Object-oriented API.
-->


<!--
#### Mixing sync and async in a single client

PyJapc gives an optional ``callback`` argument, allowing you to go from a synchronous get to an asynchronous one
-->


<!--
#### More control of threads

TODO
Include:
 * CallbackClient thread-pool
 * AsyncIO event loop running (and the fact that JAPC is creating a thread-pool under the hood)
 * ...
-->


<!--
#### Get / Set round-trip

TODO
-->


<!--
#### Swappable data sources (providers)

Provider
-->


<!--
#### Middleware to influence a subscription stream

e.g. for Grouping/Synchronisation
-->


<!--
#### Simulation mode

Allow swapping the backend out...
-->


### Known limitations, design decisions and related future plans (non-exhaustive)

#### Keyword only arguments

We have currently made all of our key interfaces keyword-only.
As we gain more experience of the interface and how it is used, we expect to loosen this in the future.


#### Ability to set a default selector for a client

In PyJapc it is possible to pass a selector to the constructor, and have that used as the default for
subsequent get/set/subscribes. It is clear that this API is convenient, and is liked, but it presents
challenges for things such as thread-safety and client isolation. We anticipate reviewing this further
during the course of the prototype development - it is hoped that we can mitigate this particular
API through the addition of an object-oriented API (which is implicitly stateful) for example.

In the meantime, a quick (but not necessarily convenient) workaround would be to use a functools partial:

```python
import functools.partial

new_setter = functools.partial(client.set, selector=the_default_selector)
```

The same "trick" would allow default device and property values to be set:

```python
simple_getter = functools.partial(client.get, selector=the_default_selector, device='my-device', prop='my-property')

print(simple_getter().value)
```

#### InCA

PyJapc used to configure InCA in initializer based on the arguments supplied. This lead to often confusing
behavior. While PyDA does not currently provide a convenient way of configuring InCA, it's possible to
access the routine that enables it:

```python
import pyda_japc
import pyda
from pyda_japc._provider import enable_inca

enable_inca()
client = pyda.CallbackClient(provider=pyda_japc.JapcProvider())
...
```

API is not completely polished, hence a private import is required at the moment.

Note, that `enable_inca` does not accept any arguments. While PyJapc would try to configure InCA for a
specific InCA server based on the given timing user, this has no real benefit, since only the first
request is given to a fixed server, while then routing is optimized automatically. Hence, `pyda_japc`
uses the default resolution to configure InCA.

This operation is also cannot be rolled back due to the way how InCA configurator works.

#### No more timezone state

In PyJapc, it is possible to pass a timezone to the constructor, which will influence `datetime` objects
stored in the value headers. PyDA does not allow it. While value headers also have a convenience accessor
producing `datetime` objects, they are always created with UTC timezone.

#### NoSet

PyJapc allows a safe-mode operation via `noSet=True` constructor argument, which effectively replaces
all SET operations with a log output of what would be actually done, sort of a dry-run. PyDA does not
include this capability.

<!--
#### Properties not parameters

In JAPC a parameter can be either a device property, or a field of a device property.

-->

#### Complex data structures not there yet

Current data model implementation does not support complex data structures, such as enums,
functions and function lists.


<!--
#### Property specific casting

In PyJapc Python type conversion is based on information from a "property descriptor".
In PyDA we do not currently expose such information, and therefore are currently only able to do a naive type conversion.
-->

<!--
#### Looser RBAC API coupling

PyJapc includes APIs for RBAC authentication. PyDA doesn't ... TODO
-->
