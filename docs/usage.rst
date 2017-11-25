Reporting exceptions
====================

When an exception is caught, the typical course of action is to log it::

    async with Context() as ctx:
        ...
        try:
            do_something()
        except Exception:
            logger.exception('Tried to do something but it failed :(')

To take advantage of the exception reporters configured with this component, all you have to do is
call :func:`~asphalt.exceptions.report_exception` instead::

    from asphalt.exceptions import report_exception


    async with Context() as ctx:
        ...
        try:
            do_something()
        except Exception:
            report_exception(ctx, 'Tried to do something but it failed :(')

This will not only log the exception as usual, but also send it to any external services
represented by the configured exception reporter backends.

The ``ctx`` argument is required in order for the function to find the configured exception
reporter resources. Additionally, it looks up plugins matching the fully qualified class name of
the context object to provide additional information to each exception reporter backend.
