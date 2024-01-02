from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from typing import Any, Sequence

import sentry_sdk
from asphalt.core import Context, resolve_reference
from sentry_sdk.integrations import Integration

from asphalt.exceptions.api import ExceptionReporter

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

logger = logging.getLogger(__name__)

Event: TypeAlias = "dict[str, Any]"
Hint: TypeAlias = "dict[str, Any]"
Breadcrumb: TypeAlias = "dict[str, Any]"
BreadcrumbHint: TypeAlias = "dict[str, Any]"
EventProcessor: TypeAlias = "Callable[[Event, Hint], Event | None]"
BreadcrumbProcessor: TypeAlias = "Callable[[Breadcrumb, BreadcrumbHint], Breadcrumb | None]"


class SentryExceptionReporter(ExceptionReporter):
    """
    Reports exceptions using the Sentry_ service.

    To use this backend, install asphalt-exceptions with the ``sentry`` extra.

    All keyword arguments are directly passed to :func:`sentry_sdk.init`.
    The following defaults are set for the client arguments:

    * environment: "development" or "production", depending on the ``__debug__`` flag

    Integrations can be added via the ``integrations`` option which is a list where each item is
    either an object that implements the :class:`sentry_sdk.integrations.Integration` interface,
    or a dictionary where the ``type`` key is a module:varname reference to a class implementing
    the aforementioned interface. The ``args`` key, when present, should be a sequence that is
    passed to the integration as positional arguments, while the ``kwargs`` key, when present,
    should be a mapping of keyword arguments to their values.

    The extras passed to this backend are passed to :func:`sentry_sdk.capture_exception` as keyword
    arguments. Two such options have been special cased and can be looked up as a
    ``module:varname`` reference:

    - ``before_send``
    - ``before_breadcrumb``

    For more information, see the `Sentry SDK documentation`_.

    .. _Sentry: https://sentry.io/
    .. _Sentry SDK documentation: https://docs.sentry.io/platforms/python/
    """

    def __init__(
        self,
        integrations: Sequence[Integration | dict[str, Any]] = (),
        before_send: EventProcessor | str | None = None,
        before_breadcrumb: BreadcrumbProcessor | str | None = None,
        **options,
    ) -> None:
        if isinstance(before_send, str):
            _before_send: EventProcessor | None = resolve_reference(before_send)
        else:
            _before_send = before_send

        if isinstance(before_breadcrumb, str):
            _before_breadcrumb: BreadcrumbProcessor | None = resolve_reference(before_breadcrumb)
        else:
            _before_breadcrumb = before_breadcrumb

        options.setdefault("environment", "development" if __debug__ else "production")

        integrations_: list[Integration] = []
        for integration in integrations:
            if isinstance(integration, dict):
                integration_class = resolve_reference(integration["type"])
                integration = integration_class(
                    *integration.get("args", ()), **integration.get("kwargs", {})
                )

            integrations_.append(integration)

        sentry_sdk.init(
            integrations=integrations_,
            before_send=_before_send,
            before_breadcrumb=_before_breadcrumb,
            **options,
        )

    def report_exception(
        self,
        ctx: Context,
        exception: BaseException,
        message: str,
        extra: dict[str, Any],
    ) -> None:
        sentry_sdk.capture_exception(exception, **extra)
