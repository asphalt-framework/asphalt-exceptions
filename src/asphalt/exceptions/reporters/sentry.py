import logging
from typing import Dict, Any

from asphalt.core import Context
from raven import Client
from raven_aiohttp import AioHttpTransport

from asphalt.exceptions.api import ExceptionReporter

logger = logging.getLogger(__name__)


class SentryExceptionReporter(ExceptionReporter):
    """
    Reports exceptions using the Sentry_ service.

    To use this backend, install asphalt-exceptions with the ``sentry`` extra.

    All keyword arguments are directly passed to :class:`raven.Client`.
    The following defaults are set for the client arguments:

    * environment: "development" or "production", depending on the ``__debug__`` flag
    * transport: :class:`raven_aiohttp.AioHttpTransport`
    * enable_breadcrumbs: ``False``
    * install_logging_hook: ``False``

    The extras passed to this backend are passed to :meth:`raven.Client.capture` as keyword
    arguments.

    For more information, see the `Raven client documentation`_.

    .. _Sentry: https://sentry.io/
    .. _Raven client documentation: https://docs.sentry.io/clients/python/#configuring-the-client
    """

    def __init__(self, **client_args) -> None:
        client_args.setdefault('environment', 'development' if __debug__ else 'production')
        client_args.setdefault('transport', AioHttpTransport)
        client_args.setdefault('enable_breadcrumbs', False)
        client_args.setdefault('install_logging_hook', False)
        self.client = Client(**client_args)

    def report_exception(self, ctx: Context, exception: BaseException, message: str,
                         extra: Dict[str, Any]) -> None:
        exc_info = type(exception), exception, exception.__traceback__
        self.client.captureException(exc_info, message=message, **extra)
