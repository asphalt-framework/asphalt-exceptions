from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sentry_sdk import Transport
from sentry_sdk.integrations import Integration

from asphalt.exceptions.reporters.sentry import SentryExceptionReporter

pytestmark = pytest.mark.anyio


class DummyIntegration(Integration):
    def __init__(self, arg_a: Any, arg_b: Any):
        self.arg_a = arg_a
        self.arg_b = arg_b

    @staticmethod
    def setup_once() -> None:
        pass


def before_send(event: dict[str, Any], hint: dict[str, Any]) -> None:
    pass


def before_breadcrumb(breadcrumb: dict[str, Any], hint: dict[str, Any]) -> None:
    pass


async def test_sentry() -> None:
    exception = None
    try:
        1 / 0
    except ZeroDivisionError as exc:
        exception = exc

    transport = MagicMock(Transport)
    reporter = SentryExceptionReporter(
        dsn="http://username:password@127.0.0.1/000000", transport=transport
    )
    assert exception is not None
    reporter.report_exception(exception, "test exception", {})

    transport.capture_event.assert_called_once()


def test_integrations() -> None:
    integrations: list[Integration | dict[str, Any]] = [
        DummyIntegration(1, 2),
        {"type": f"{__name__}:DummyIntegration", "args": [3], "kwargs": {"arg_b": 4}},
    ]
    SentryExceptionReporter(
        dsn="http://username:password@127.0.0.1/000000", integrations=integrations
    )


def test_hook_lookup(mocker: MockerFixture) -> None:
    init_func = mocker.patch("sentry_sdk.init")
    SentryExceptionReporter(
        before_send=f"{__name__}:before_send",
        before_breadcrumb=f"{__name__}:before_breadcrumb",
    )
    init_func.assert_called_once_with(
        integrations=[],
        before_send=before_send,
        before_breadcrumb=before_breadcrumb,
        environment="development",
    )
