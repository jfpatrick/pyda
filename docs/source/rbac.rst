RBAC support
============


Access to certain devices will inevitably be restricted. This library relies on :mod:`pyrbac` for authorization purposes.

You can supply an RBAC token to any client object and all subsequent calls will be performed with that token.

.. note:: Existing subscriptions belonging to the client will be updated with the new token.

Let's obtain a valid token using :mod:`pyrbac` first (not PyDA specific, refer to
`pyrbac documentation <https://acc-py.web.cern.ch/gitlab-mono/acc-co/cmw/cmw-core/docs/pyrbac/stable/usage.html>`_)::

    import pyrbac

    rbac_client = pyrbac.AuthenticationClient.create()
    try:
        token = rbac_client.login_explicit("aeinstein", "YouNeverFailUntilYouStopTrying123")
    except pyrbac.AuthenticationError as e:
        print(e)
    else:
        ...

Now we must set the token to the provider::

    import pyda
    import pyda_japc

    pyda_client = pyda.SimpleClient(provider=pyda_japc.JapcProvider(rbac_token=token))
    sub = pyda_client.subscribe(device='SOME.PROTECTED.DEVICE',
                                prop='SomeProtectedProperty',
                                selector='SOME.TIMING.USER')
    sub.start()

.. note:: RBAC tokens are stored on the provider level. Therefore, it is possible to use different tokens when
          working with multiple sources of data. In case of Java-backed :class:`~pyda_japc.JapcProvider`,
          it is a special singleton provider, therefore all calls to the devices via JAPC interface use the same
          RBAC token.

To replace existing token with a new one, update it on the provider level::

    ...
    pyda_client.provider.rbac_token = my_new_token

.. note:: Existing JAPC/RDA3 subscriptions do not pick up a new token until they are recreated. Should there be a
          trigger for the underlying system to re-create subscriptions, the new token will be used. This behavior
          is not defined by PyDA and comes from the underlying system.
