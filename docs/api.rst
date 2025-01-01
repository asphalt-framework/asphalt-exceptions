API reference
=============

.. py:currentmodule:: asphalt.exceptions

Component
---------

.. autoclass:: ExceptionReporterComponent

Functions
---------

.. autofunction:: report_exception

Interfaces
----------

.. autoclass:: ExceptionReporter
.. autoclass:: ExtrasProvider

Exception reporters
-------------------

.. autoclass:: asphalt.exceptions.reporters.sentry.SentryExceptionReporter
.. autoclass:: asphalt.exceptions.reporters.raygun.RaygunExceptionReporter
