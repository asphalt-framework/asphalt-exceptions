from __future__ import annotations

import logging
from asyncio import AbstractEventLoop, get_running_loop
from collections.abc import AsyncGenerator, Mapping
from typing import Any

from asphalt.core import (
    Component,
    PluginContainer,
    add_resource,
    context_teardown,
    merge_config,
    qualified_name,
)

from ._api import ExceptionReporter
from ._utils import report_exception

reporter_backends = PluginContainer("asphalt.exceptions.reporters", ExceptionReporter)
logger = logging.getLogger(__name__)


def default_exception_handler(loop: AbstractEventLoop, context: dict[str, Any]) -> None:
    if "exception" in context:
        report_exception(context["message"], context["exception"])


class ExceptionReporterComponent(Component):
    """
    Creates one or more :class:`~asphalt.exceptions.api.ExceptionReporter` resources.

    These resources are used by :func:`~asphalt.exceptions.report_exception` which calls
    each one of them to report the exception.

    Optionally (and by default), a default exception handler is also installed for the
    event loop which calls :func:`~asphalt.exceptions.report_exception` for all
    exceptions that occur in the event loop machinery or in tasks which are garbage
    collected without ever having been awaited on.

    Exception reporters can be configured in two ways:

    #. a single reporter, with configuration supplied directly as keyword arguments to
        this component's constructor
    #. multiple reporters, by providing the ``reporters`` option where each key is the
        resource name and each value is a dictionary containing that reporter's
        configuration

    Each exception reporter configuration has one special option that is not passed to
    the constructor of the backend class:

    * backend: entry point name of the reporter backend class (required)

    :param reporters: a dictionary of resource name ⭢ constructor arguments for the
        chosen reporter class
    :param install_default_handler: ``True`` to install a new default exception handler
        for the event loop when the component starts
    :param default_args: default values for constructor keyword arguments
    """

    def __init__(
        self,
        reporters: Mapping[str, dict[str, Any] | None] | None = None,
        install_default_handler: bool = True,
        **default_args: Any,
    ) -> None:
        self.install_default_handler = install_default_handler
        if not reporters:
            reporters = {"default": default_args}

        self.reporters: list[tuple[str, ExceptionReporter]] = []
        for resource_name, config in reporters.items():
            merged_config = merge_config(default_args, config or {})
            type_ = merged_config.pop("backend", resource_name)
            reporter = reporter_backends.create_object(type_, **merged_config)
            self.reporters.append((resource_name, reporter))

    @context_teardown
    async def start(self) -> AsyncGenerator[None, Exception | None]:
        for resource_name, reporter in self.reporters:
            types: list[type] = [ExceptionReporter, type(reporter)]
            add_resource(reporter, resource_name, types=types)
            logger.info(
                "Configured exception reporter (%s; class=%s)",
                resource_name,
                qualified_name(reporter),
            )

        if self.install_default_handler:
            get_running_loop().set_exception_handler(default_exception_handler)
            logger.info("Installed default event loop exception handler")

            yield

            get_running_loop().set_exception_handler(None)
            logger.info("Uninstalled default event loop exception handler")
