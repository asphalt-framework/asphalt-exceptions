import inspect
import logging
import sys
from contextlib import suppress
from typing import Union, Dict, Any  # noqa: F401

from asphalt.core import Context, qualified_name, PluginContainer
from raven import Client
from typeguard import check_argument_types

metadata_providers = PluginContainer('asphalt.sentry.metadata_providers')


def report_exception(message: str = None, exception: BaseException = None, *, ctx: Context = None,
                     client: Client = None, logger: Union[str, logging.Logger] = None) -> None:
    """
    Report an exception to Sentry and optionally log it locally as well.

    :param ctx: context object to use for adding tags and other contextual information to the
        report, as well as for retrieving the sentry client object
    :param message: if specified, emit a log entry too
    :param exception: the exception to report; retrieved from :func:`sys.exc_info` if omitted
    :param logger: a logger object or the name of the logger to use if ``log_message`` was given
    :param client: the Sentry client to use (retrieved from ``ctx`` if omitted)

    """
    assert check_argument_types()

    # Sanity checks
    if exception:
        exc_info = type(exception), exception, exception.__traceback__
    else:
        exc_info = sys.exc_info()
        if not exc_info[0]:
            raise Exception(
                'missing "exception" parameter and no current exception context available')

    # If no Client was supplied but a Context was, try to get the Client resource from it
    if not client and ctx:
        client = client or ctx.get_resource(Client)

    # If there is a contextual information provider plugin for this context class, run it
    extra = {}  # type: Dict[str, Any]
    if ctx:
        with suppress(LookupError):
            provider = metadata_providers.resolve(qualified_name(ctx))
            extra = provider(ctx)

    # First log the error (if a log message was given)
    if message:
        if logger is None:
            # Try to get the caller's module name
            module = inspect.getmodule(inspect.currentframe().f_back)
            logger = getattr(module, '__name__', None)
        if isinstance(logger, str):
            logger = logging.getLogger(logger)
        if logger is None:
            raise Exception('missing "logger" parameter')

        logger.error(message, exc_info=exc_info)

    # Then report it to Sentry (if a client could be obtained)
    if client:
        client.captureException(exc_info, message=message, extra=extra)
