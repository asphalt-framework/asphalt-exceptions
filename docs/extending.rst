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
subclassing :class:`~asphalt.exceptions.api.ExtrasProvider` and adding one or more instances of it
as resources to the context.

For example, if you wanted to provide extra data for Sentry about your custom context
(``MyContext``), you could do write a provider like this::

    from asphalt.exceptions.api import ExtrasProvider
    from asphalt.exceptions.reporters.sentry import SentryExceptionReporter


    class MyExtrasProvider(ExtrasProvider):
        def get_extras(ctx, reporter):
            if isinstance(ctx, MyContext) and isinstance(reporter, SentryExceptionReporter):
                return {
                    'time_spent': 1265,
                    'data': {
                        'user': {'email': 'foo@example.org'}
                    },
                    'tags': {'site': 'example.org'},
                    'extra': {'foo': 'bar'}
                }

And then during the startup of your component::

    from asphalt.exceptions.api import ExtrasProvider


    class MyComponent(Component):
        ...
        async def start(ctx):
            ...
            ctx.add_resource(MyExtrasProvider(), types=[ExtrasProvider])
