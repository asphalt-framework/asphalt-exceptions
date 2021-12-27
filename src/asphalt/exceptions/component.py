import logging
from functools import partial
from typing import Dict, Optional, Any, List, Tuple  # noqa: F401

from asphalt.core import (
    Component, Context, merge_config, PluginContainer, qualified_name, context_teardown)
from async_generator import yield_
from typeguard import check_argument_types

from asphalt.exceptions import report_exception
from asphalt.exceptions.api import ExceptionReporter

reporter_backends = PluginContainer('asphalt.exceptions.reporters', ExceptionReporter)
logger = logging.getLogger(__name__)


def default_exception_handler(loop, context: Dict[str, Any], *, ctx: Context) -> None:
    report_exception(ctx, context['message'], context['exception'])


class ExceptionReporterComponent(Component):
    """
    Creates one or more :class:`~asphalt.exceptions.api.ExceptionReporter` resources.

    These resources are used by :func:`~asphalt.exceptions.report_exception` which calls each one
    of them to report the exception.

    Optionally (and by default), a default exception handler is also installed for the event loop
    which calls :func:`~asphalt.exceptions.report_exception` for all exceptions that occur in the
    event loop machinery or in tasks which are garbage collected without ever having been awaited
    on.

    Exception reporters can be configured in two ways:

    #. a single reporter, with configuration supplied directly as keyword arguments to this
        component's constructor
    #. multiple reporters, by providing the ``reporters`` option where each key is the resource
        name and each value is a dictionary containing that reporter's configuration

    Each exception reporter configuration has one special option that is not passed to the
    constructor of the backend class:

    * backend: entry point name of the reporter backend class (required)

    :param reporters: a dictionary of resource name ⭢ constructor arguments for the chosen
        reporter class
    :param install_default_handler: ``True`` to install a new default exception handler for the
        event loop when the component starts
    :param default_args: default values for constructor keyword arguments
    """

    def __init__(self, reporters: Dict[str, Optional[Dict[str, Any]]] = None,
                 install_default_handler: bool = True, **default_args) -> None:
        assert check_argument_types()
        self.install_default_handler = install_default_handler
        if not reporters:
            reporters = {'default': default_args}

        self.reporters = []  # type: List[Tuple]
        for resource_name, config in reporters.items():
            config = merge_config(default_args, config or {})
            type_ = config.pop('backend', resource_name)
            serializer = reporter_backends.create_object(type_, **config)
            self.reporters.append((resource_name, serializer))

    @context_teardown
    async def start(self, ctx: Context) -> None:
        for resource_name, reporter in self.reporters:
            types = [ExceptionReporter, type(reporter)]
            ctx.add_resource(reporter, resource_name, types=types)
            logger.info('Configured exception reporter (%s; class=%s)', resource_name,
                        qualified_name(reporter))

        if self.install_default_handler:
            handler = partial(default_exception_handler, ctx=ctx)
            ctx.loop.set_exception_handler(handler)
            logger.info('Installed default event loop exception handler')
            await yield_()
            ctx.loop.set_exception_handler(None)
            logger.info('Uninstalled default event loop exception handler')
