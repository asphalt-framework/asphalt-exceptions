import asyncio
from unittest.mock import patch

import pytest
from asphalt.core import Context

from asphalt.exceptions.reporters.sentry import SentryExceptionReporter


@pytest.mark.asyncio
async def test_sentry():
    exception = None
    try:
        1 / 0
    except ZeroDivisionError as exc:
        exception = exc

    reporter = SentryExceptionReporter(dsn='http://username:password@127.0.0.1/000000')
    with patch.object(reporter.client, 'send') as send:
        reporter.report_exception(Context(), exception, 'test exception', {})

    await asyncio.sleep(0.1)
    assert send.call_count == 1
