from unittest.mock import patch

import pytest
from anyio import sleep

from asphalt.exceptions.reporters.raygun import RaygunExceptionReporter

pytestmark = pytest.mark.anyio


async def test_raygun() -> None:
    exception = None
    try:
        1 / 0
    except ZeroDivisionError as exc:
        exception = exc

    reporter = RaygunExceptionReporter("abvcgrdg234")
    with patch.object(reporter.client, "_post") as post:
        assert exception is not None
        reporter.report_exception(exception, "test exception", {})

    await sleep(0.1)
    assert post.call_count == 1
