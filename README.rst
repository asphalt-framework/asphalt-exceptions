.. image:: https://travis-ci.org/asphalt-framework/asphalt-exceptions.svg?branch=master
  :target: https://travis-ci.org/asphalt-framework/asphalt-exceptions
  :alt: Build Status
.. image:: https://coveralls.io/repos/github/asphalt-framework/asphalt-exceptions/badge.svg?branch=master
  :target: https://coveralls.io/github/asphalt-framework/asphalt-exceptions?branch=master
  :alt: Code Coverage

This Asphalt framework component provides a pluggable means to send exception reports to external
services. Optionally, it can also install itself as the default handler for exceptions occurring in
the event loop.

The following backends are provided out of the box:

* Sentry_
* Raygun_
* Standard library logging

Plugins can also be written to provide context specific custom data for each backend.

.. _Sentry: http://sentry.io/
.. _Raygun: https://raygun.com/

Project links
-------------

* `Documentation <http://asphalt-exceptions.readthedocs.org/en/latest/>`_
* `Help and support <https://github.com/asphalt-framework/asphalt/wiki/Help-and-support>`_
* `Source code <https://github.com/asphalt-framework/asphalt-exceptions>`_
* `Issue tracker <https://github.com/asphalt-framework/asphalt-exceptions/issues>`_
