pyda
====

Introduction
------------

PyDA is a Pythonic, `device-property
<https://be-dep-co.web.cern.ch/sites/be-dep-co.web.cern.ch/files/Introduction_to_the_BE-CO_Control_System.pdf>`_
model based, API for accessing device data.


Installation
------------
Using the `acc-py Python package index
<https://wikis.cern.ch/display/ACCPY/Getting+started+with+acc-python#Gettingstartedwithacc-python-OurPythonPackageRepositoryrepo>`_
:mod:`pyda` can be pip installed with::

   pip install pyda

.. warning:: "pyda" is a working prototype name and is likely to change before the stable release

PyDA is bound to utilize pluggable data providers, therefore you likely will need to install the provider.

.. note:: At this point, we aim to provide JPype-based JAPC provider as the first available type

All possible providers are deliberately not bundled into PyDA, since they may have very specific dependencies (e.g.
Java libraries for JPype-based providers).

If you wish to install the JAPC device provider, please include an additional dependency (``pyda-japc``) when
installing PyDA::

   pip install pyda pyda-japc


Documentation contents
----------------------

.. toctree::
    :maxdepth: 1
    :hidden:

    self

.. toctree::
    :caption: pyda
    :maxdepth: 1

    usage
    async_usage
    rbac
    about_this_prototype

.. toctree::
    :caption: Reference docs
    :maxdepth: 1

    api
    genindex
