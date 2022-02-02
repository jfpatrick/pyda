pyda
====

Introduction
------------

PyDA is a Pythonic, `device-property <https://be-dep-co.web.cern.ch/sites/be-dep-co.web.cern.ch/files/Introduction_to_the_BE-CO_Control_System.pdf>`_ model based, API for accessing device data.

Installation
------------
Using the `acc-py Python package index
<https://wikis.cern.ch/display/ACCPY/Getting+started+with+acc-python#Gettingstartedwithacc-python-OurPythonPackageRepositoryrepo>`_
``pyda`` can be pip installed with (WARNING: THIS DOESN'T WORK, AND IS A NAME THAT WILL COLLIDE WITH THE OUTSIDE WORLD)::
   pip install pyda

If you wish to install the JAPC device provider, please also include that extra when installing PyDA::

   pip install pyda[japc-provider]


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
    async_client

.. toctree::
    :caption: Reference docs
    :maxdepth: 1

    api
    genindex

