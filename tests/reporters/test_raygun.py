import asyncio
from unittest.mock import patch

import pytest
from asphalt.core import Context

from asphalt.exceptions.reporters.raygun import RaygunExceptionReporter


@pytest.mark.asyncio
async def test_raygun():
    exception = None
    try:
        1 / 0
    except ZeroDivisionError as exc:
        exception = exc

    reporter = RaygunExceptionReporter('abvcgrdg234')
    with patch.object(reporter.client, '_post') as post:
        reporter.report_exception(Context(), exception, 'test exception', {})

    await asyncio.sleep(0.1)
    assert post.call_count == 1
