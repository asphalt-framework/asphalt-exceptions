Configuration
=============

.. highlight:: yaml

You will need to install the library with the appropriate extras in order to use the backend you
want. For example, to use the Sentry backend, do this:

.. code-block:: bash

    pip install asphalt-exceptions[sentry]

The minimal configuration for Sentry integration would be like this::

    components:
      exceptions:
        backend: sentry
        dsn: https://d8e5bbc3aca4bccfc09690fd4cae45a3:47d2ecdd2bec818861db1db62cafd8d4@sentry.io/111111

And if you want to use Raygun instead::

    components:
      exceptions:
        backend: raygun
        api_key: your_api_key_here

Multiple backends
-----------------

You are not limited to using just one backend. To configure multiple backends, you can do this::

    components:
      exceptions:
        reporters:
          sentry:
            dsn: https://d8e5bbc3aca4bccfc09690fd4cae45a3:47d2ecdd2bec818861db1db62cafd8d4@sentry.io/111111
          raygun:
            api_key: your_api_key_here

Consult the :ref:`API documentation <modindex>` of each backend class for details on the
configuration options.
