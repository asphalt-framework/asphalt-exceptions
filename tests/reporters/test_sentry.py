from unittest.mock import MagicMock

import pytest
from asphalt.core import Context
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
