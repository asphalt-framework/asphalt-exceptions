import logging
from asyncio import AbstractEventLoop
from typing import Dict, Any

from asphalt.core import Component, Context, context_teardown
from async_generator import yield_
from raven import Client
from raven_aiohttp import AioHttpTransport

from asphalt.sentry.utils import report_exception

logger = logging.getLogger(__name__)


class SentryComponent(Component):
    """
    Creates a :class:`raven.Client` and installs an asyncio default exception handler which
    catches all exceptions that were never retrieved from Futures or Tasks.

    All keyword arguments are directly passed to :class:`raven.Client`.
    The following defaults are set for the client arguments:

    * environment: "development" or "production", depending on the ``__debug__`` flag
    * transport: :class:`raven_aiohttp.AioHttpTransport`
    * enable_breadcrumbs: ``False``
    * install_logging_hook: ``False``

    For more information, see the `Raven client documentation`_.

    .. _Raven client documentation: https://docs.sentry.io/clients/python/#configuring-the-client
    """

    def __init__(self, **client_args) -> None:
        client_args.setdefault('environment', 'development' if __debug__ else 'production')
        client_args.setdefault('transport', AioHttpTransport)
        client_args.setdefault('enable_breadcrumbs', False)
        client_args.setdefault('install_logging_hook', False)
        self.client_args = client_args
        self.client = Client(**client_args)

    @context_teardown
    async def start(self, ctx: Context) -> None:
        ctx.add_resource(self.client)
        ctx.loop.set_exception_handler(self.exception_handler)
        logger.info('Started Sentry integration')

        await yield_()

        ctx.loop.set_exception_handler(None)
        logger.info('Stopped Sentry integration')

    def exception_handler(self, loop: AbstractEventLoop, context: Dict[str, Any]) -> None:
        loop.default_exception_handler(context)
        report_exception(None, context['exception'], client=self.client)
