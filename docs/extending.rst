Extending asphalt-exceptions
============================

Writing new reporter backends
-----------------------------

To support new exception reporting services, you can subclass the
:class:`~asphalt.exceptions.api.ExceptionReporter` class. You just need to implement the
:meth:`~asphalt.exceptions.api.ExceptionReporter.report_exception` method.

If you want your exception reporter to be available as a backend for
:class:`~asphalt.exceptions.component.ExceptionReporterComponent`, you need to add the
corresponding entry point for it. Suppose your exception reporter class is named
``MyExceptionReporter`` and it lives in the package
``foo.bar.myreporter`` and you want to give it the alias ``myreporter``, then add this line to your
project's ``setup.py`` under the ``entry_points`` argument in the ``asphalt.exceptions.reporters``
namespace::

    setup(
        # (...other arguments...)
        entry_points={
            'asphalt.exceptions.reporters': [
                'myreporter = foo.bar.myreporter:MyExceptionReporter'
            ]
        }
    )


Or in ``setup.cfg``:

.. code-block:: ini

    [options.entry_points]
    asphalt.exceptions.reporters =
        myreporter = foo.bar.myreporter:MyExceptionReporter


Writing extras providers
------------------------

If you want to provide backend specific extra data for exception reporting, you can do so by
writing an extras provider callback and registering it as an entry point in the
``asphalt.exceptions.extras_providers`` namespace. Such callbacks always target a specific
:class:`~asphalt.core.context.Context` subclass. For example, suppose you had a context class named
``foo.bar.MyContext`` and you had written an extras provider function as follows::

    from asphalt.exceptions.reporters.sentry import SentryExceptionReporter


    def my_context_extras(context, reporter_class):
        if issubclass(reporter_class, SentryExceptionReporter):
            return {}

Then you would add an entry point for it in ``setup.py``::

    setup(
        # (...other arguments...)
        entry_points={
            'asphalt.exceptions.extras_providers': [
                'foo.bar.MyContext = foo.bar:my_context_extras'
            ]
        }
    )

Or in ``setup.cfg``:

.. code-block:: ini

    [options.entry_points]
    asphalt.exceptions.extras_providers =
        foo.bar.MyContext = foo.bar:my_context_extras
