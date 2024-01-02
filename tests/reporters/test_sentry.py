from unittest.mock import MagicMock

import pytest
from asphalt.core import Context
from pytest_mock import MockerFixture
from sentry_sdk import Transport
from sentry_sdk.integrations import Integration

from asphalt.exceptions.reporters.sentry import SentryExceptionReporter


class DummyIntegration(Integration):
    def __init__(self, arg_a, arg_b):
        self.arg_a = arg_a
        self.arg_b = arg_b

    @staticmethod
    def setup_once():
        pass


def before_send(event, hint):
    pass


def before_breadcrumb(breadcrumb, hint):
    pass


@pytest.mark.asyncio
async def test_sentry():
    exception = None
    try:
        1 / 0
    except ZeroDivisionError as exc:
        exception = exc

    transport = MagicMock(Transport)
    reporter = SentryExceptionReporter(
        dsn="http://username:password@127.0.0.1/000000", transport=transport
    )
    reporter.report_exception(Context(), exception, "test exception", {})

    transport.capture_event.assert_called_once()


def test_integrations():
    integrations = [
        DummyIntegration(1, 2),
        {"type": f"{__name__}:DummyIntegration", "args": [3], "kwargs": {"arg_b": 4}},
    ]
    SentryExceptionReporter(
        dsn="http://username:password@127.0.0.1/000000", integrations=integrations
    )


def test_hook_lookup(mocker: MockerFixture):
    init_func = mocker.patch("sentry_sdk.init")
    SentryExceptionReporter(
        before_send=f"{__name__}:before_send", before_breadcrumb=f"{__name__}:before_breadcrumb"
    )
    init_func.assert_called_once_with(
        integrations=[],
        before_send=before_send,
        before_breadcrumb=before_breadcrumb,
        environment="development",
    )
